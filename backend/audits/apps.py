"""
App configuration for the 'audits' Django app.

Provides the AuditLog model and the log_event() utility function.
Other apps import log_event() to record user actions for the audit trail.
"""
from django.apps import AppConfig


class AuditsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audits'
