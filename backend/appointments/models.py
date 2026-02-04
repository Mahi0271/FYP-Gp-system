from django.conf import settings
from django.db import models


class Appointment(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments_as_patient",
    )
    gp = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="appointments_as_gp",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    reason = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} @ {self.start_time} ({self.status})"
