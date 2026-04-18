"""
Database model for GP appointments.

An Appointment links a PATIENT user to a GP user for a specific time slot.
The lifecycle of an appointment follows these status transitions:

  REQUESTED → CONFIRMED → COMPLETED
  REQUESTED → CANCELLED
  CONFIRMED → CANCELLED

Rules enforced by the serializer (appointments/serializers.py):
  - Patients can only cancel (REQUESTED → CANCELLED)
  - GPs can only mark as complete (CONFIRMED → COMPLETED)
  - Receptionists/managers can confirm or cancel
  - No one can change a COMPLETED appointment
  - A GP cannot have two overlapping appointments
"""
from django.conf import settings
from django.db import models


class Appointment(models.Model):
    """
    A single appointment slot between a patient and a GP doctor.

    Both patient and gp reference the same User model — Django uses
    the related_name to distinguish the two foreign keys when querying.
    (e.g. user.appointments_as_patient.all()  vs  user.appointments_as_gp.all())
    """

    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"   # Patient has asked for an appointment
        CONFIRMED = "CONFIRMED", "Confirmed"   # Receptionist has confirmed the slot
        CANCELLED = "CANCELLED", "Cancelled"   # Cancelled by patient or staff
        COMPLETED = "COMPLETED", "Completed"   # GP has marked the appointment as done

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,                    # deleting the patient deletes their appointments
        related_name="appointments_as_patient",
    )
    gp = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,                   # deleting a GP leaves orphan appointments (null gp)
        null=True,
        blank=True,
        related_name="appointments_as_gp",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REQUESTED)
    reason = models.CharField(max_length=255, blank=True)  # brief description of why the patient is coming in

    created_at = models.DateTimeField(auto_now_add=True)  # set once when the row is first inserted

    def __str__(self):
        return f"{self.patient.username} @ {self.start_time} ({self.status})"
