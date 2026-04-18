"""
Database models for user accounts and role-based profiles.

The system has four types of users, each with a distinct role:
  - PATIENT       → books appointments, views their own medical record
  - RECEPTIONIST  → manages appointments and patient contact details
  - GP            → views and writes clinical entries for assigned patients
  - PRACTICE_MANAGER → views the dashboard, audit logs, and system metrics

When a new GP user is created, a GPProfile is automatically created by a
signal in signals.py.  When a new PATIENT is created, a PatientProfile is
created and the patient is automatically assigned to the GP with the fewest
current patients (load-balanced round-robin via signals.py).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends Django's built-in AbstractUser.

    We add a 'role' field so the application knows what a user is allowed
    to do, and MFA fields so users can protect their account with a
    time-based one-time password (TOTP) via an authenticator app.
    """

    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        RECEPTIONIST = "RECEPTIONIST", "Receptionist"
        GP = "GP", "GP Doctor"
        PRACTICE_MANAGER = "PRACTICE_MANAGER", "Practice Manager"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.PATIENT,
    )

    # MFA (Multi-Factor Authentication) using TOTP (e.g. Google Authenticator)
    mfa_enabled = models.BooleanField(default=False)        # True once the user has verified their first code
    mfa_secret = models.CharField(max_length=64, blank=True, default="")  # Base32 seed for the TOTP algorithm


class GPProfile(models.Model):
    """
    Extra information attached to a GP user.

    The reverse relation 'gp_profile.patients' gives all PatientProfiles
    assigned to this GP.  Created automatically by a post_save signal.
    """
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="gp_profile")

    def __str__(self):
        return f"GP: {self.user.username}"


class PatientProfile(models.Model):
    """
    Extra information attached to a PATIENT user.

    Holds the patient's contact details and a link to their assigned GP.
    If the GP is deleted the field becomes NULL (the patient is not deleted).
    Created automatically by a post_save signal on User.
    """
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="patient_profile")
    assigned_gp = models.ForeignKey(
        "accounts.GPProfile",
        on_delete=models.SET_NULL,  # removing a GP doesn't remove their patients
        null=True,
        blank=True,
        related_name="patients",    # lets you do gp_profile.patients.all()
    )

    # Contact and demographic details — all optional so partial updates work
    phone = models.CharField(max_length=30, blank=True, default="")
    address_line1 = models.CharField(max_length=255, blank=True, default="")
    address_line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    postcode = models.CharField(max_length=20, blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Patient: {self.user.username}"