"""
Django signals for the records app.

Wires up one automatic behaviour:
  post_save on PatientProfile → create_medical_record_for_patient
    When a new PatientProfile is created (which itself happens via a signal
    in accounts/signals.py when a PATIENT user is registered), automatically
    create an empty MedicalRecord for that patient.

This ensures every patient always has a medical record waiting for them
before the GP ever needs to write an entry — no manual setup required.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import PatientProfile
from .models import MedicalRecord


@receiver(post_save, sender=PatientProfile)
def create_medical_record_for_patient(sender, instance: PatientProfile, created: bool, **kwargs):
    """
    Automatically provision an empty MedicalRecord when a PatientProfile is first created.

    get_or_create is used defensively — if a record somehow already exists
    (e.g. from a data migration or admin action), we skip creation silently.
    """
    if not created:
        return  # only run on INSERT, not on profile updates

    MedicalRecord.objects.get_or_create(patient=instance.user)
