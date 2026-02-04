from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    role = models.CharField(max_length=32, blank=True, default="")
    action = models.CharField(max_length=64)
    object_type = models.CharField(max_length=64, blank=True, default="")
    object_id = models.IntegerField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp} {self.action} {self.object_type}:{self.object_id}"
