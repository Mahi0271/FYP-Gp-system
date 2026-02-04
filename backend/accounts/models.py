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

    def __str__(self):
        return f"Patient: {self.user.username}"