"""
App configuration for the 'appointments' Django app.

Handles appointment booking, GP availability, and status management.
"""
from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appointments'
