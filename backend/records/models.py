"""
Database models for the medical records system.

Structure:
  MedicalRecord — one per patient, acts as a container/folder
    └── ClinicalEntry (many) — individual notes, diagnoses, or prescriptions

Encryption:
  The text content of every ClinicalEntry is encrypted at rest using
  PostgreSQL's pgcrypto extension (pgp_sym_encrypt / pgp_sym_decrypt).
  The plaintext 'content' column is always cleared to '' after the
  encrypted version is written to 'content_enc'.  The decryption
  happens in SQL (via RawSQL annotation in api_views.py) and the
  plaintext is only ever returned in API responses — it never lives
  in the database in readable form.

Access rules (enforced in api_views.py and serializers.py):
  - Patients can read their own record (read-only, no writes)
  - GPs can read and write entries for their assigned patients only
  - Receptionists and managers have no access to medical records
"""
from django.conf import settings
from django.db import models


class MedicalRecord(models.Model):
    """
    The top-level container for a patient's clinical history.

    There is exactly one MedicalRecord per patient, created automatically
    by a signal in records/signals.py when the PatientProfile is first saved.
    """
    patient = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_record",  # access via patient_user.medical_record
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # bumped automatically on every save

    def __str__(self):
        return f"MedicalRecord(patient={self.patient.username})"


class ClinicalEntry(models.Model):
    """
    A single clinical note, diagnosis, or prescription written by a GP.

    The actual text content is stored encrypted in 'content_enc' (bytea column).
    The 'content' column is always an empty string in the database — it is only
    used as a write-only input channel in the serializer so the API stays simple.

    When you read entries through the API, the serializer's to_representation()
    replaces the empty 'content' with the decrypted value from the SQL annotation.
    """

    class EntryType(models.TextChoices):
        NOTE = "NOTE", "Note"
        DIAGNOSIS = "DIAGNOSIS", "Diagnosis"
        PRESCRIPTION = "PRESCRIPTION", "Prescription"

    record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="entries",  # access via medical_record.entries.all()
    )
    type = models.CharField(max_length=32, choices=EntryType.choices)
    title = models.CharField(max_length=255, blank=True, default="")
    content = models.TextField(blank=True, default="")        # always '' in DB — plaintext input only
    content_enc = models.BinaryField(null=True, blank=True, editable=False)  # encrypted content stored here

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # preserve entries even if the GP account is deleted
        null=True,
        blank=True,
        related_name="created_clinical_entries",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # newest entries appear first

    def __str__(self):
        return f"ClinicalEntry({self.type}) for {self.record.patient.username}"
