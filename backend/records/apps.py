"""
App configuration for the 'records' Django app.

Manages encrypted medical records and clinical entries (notes, diagnoses,
prescriptions).  The ready() method imports signals so that a MedicalRecord
is automatically created whenever a new PatientProfile is saved.
"""
from django.apps import AppConfig


class RecordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'records'

    def ready(self):
        # Register the signal that auto-creates a MedicalRecord for new patients
        from . import signals  # noqa: F401
