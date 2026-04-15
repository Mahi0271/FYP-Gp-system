from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
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

    # --- MFA / TOTP ---
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True, default="")



class GPProfile(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="gp_profile")

    def __str__(self):
        return f"GP: {self.user.username}"

class PatientProfile(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name="patient_profile")
    assigned_gp = models.ForeignKey(
        "accounts.GPProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patients",
    )

    phone = models.CharField(max_length=30, blank=True, default="")
    address_line1 = models.CharField(max_length=255, blank=True, default="")
    address_line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    postcode = models.CharField(max_length=20, blank=True, default="")
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Patient: {self.user.username}"