from django.conf import settings
from django.db import models


class MedicalRecord(models.Model):
    patient = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_record",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MedicalRecord(patient={self.patient.username})"


class ClinicalEntry(models.Model):
    class EntryType(models.TextChoices):
        NOTE = "NOTE", "Note"
        DIAGNOSIS = "DIAGNOSIS", "Diagnosis"
        PRESCRIPTION = "PRESCRIPTION", "Prescription"

    record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name="entries",
    )
    type = models.CharField(max_length=32, choices=EntryType.choices)
    title = models.CharField(max_length=255, blank=True, default="")
    content = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_clinical_entries",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"ClinicalEntry({self.type}) for {self.record.patient.username}"
