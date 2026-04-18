"""
App configuration for the 'accounts' Django app.

The ready() method is called once Django has finished loading all models.
We import signals here (not at module level) to ensure all models are
available when signal receivers are registered — avoiding import errors.
"""
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # Register signal handlers (auto-create profiles, etc.) once models are loaded
        from . import signals  # noqa
