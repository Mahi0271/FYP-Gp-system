"""
Database model for the system-wide audit trail.

Every significant action in the system (login, logout, appointment created/updated,
medical record entry written, patient details changed) is recorded as an AuditLog
row by calling audits.utils.log_event() from the relevant API view.

The audit log is append-only from the application's perspective — entries are never
deleted or modified after they're written.  The practice manager can browse these
records via the /api/audits/ endpoint and the manager dashboard.

Stored per event:
  - who did it (user + role at time of action)
  - what they did (action string like "APPOINTMENT_CREATE")
  - what object was affected (type + id)
  - extra context as JSON (e.g. the new status, patient id)
  - their IP address
  - when it happened (timestamp)
"""
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """
    A single audit event.  Written once, never updated.

    If the user is deleted their foreign key becomes NULL, but the log entry
    is preserved — we never lose the history even when accounts are removed.
    """
    timestamp = models.DateTimeField(auto_now_add=True)  # set automatically to now on insert

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # keep the log entry even if the user is deleted
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    role = models.CharField(max_length=32, blank=True, default="")  # snapshot of the user's role at the time
    action = models.CharField(max_length=64)                        # e.g. "APPOINTMENT_CREATE", "LOGOUT"
    object_type = models.CharField(max_length=64, blank=True, default="")  # e.g. "appointment", "user"
    object_id = models.IntegerField(null=True, blank=True)          # primary key of the affected object

    metadata = models.JSONField(default=dict, blank=True)           # any extra context (status, ids, etc.)
    ip_address = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["-timestamp"]  # newest events first in list views

    def __str__(self):
        return f"{self.timestamp} {self.action} {self.object_type}:{self.object_id}"
