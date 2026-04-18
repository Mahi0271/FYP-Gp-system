"""
App configuration for the 'dashboard' Django app.

Provides a single API endpoint that aggregates cross-app metrics
(appointments, records, audits) for the practice manager's overview.
"""
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"