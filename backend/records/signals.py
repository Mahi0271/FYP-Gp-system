from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import PatientProfile
from .models import MedicalRecord


@receiver(post_save, sender=PatientProfile)
def create_medical_record_for_patient(sender, instance: PatientProfile, created: bool, **kwargs):
    if not created:
        return

    # Create record if it doesn't already exist
    MedicalRecord.objects.get_or_create(patient=instance.user)
