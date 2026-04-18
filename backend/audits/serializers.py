"""
Serializer for the AuditLog model.

This is a read-only serializer — audit logs are never created or modified
through the API, only read (by practice managers via /api/audits/).

The user_id and username fields are pulled from the related User object
using dot-notation source paths so the API response is flat and easy to
consume without extra nesting.
"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    # Flatten the nested user relationship into two simple fields
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "timestamp",
            "user_id",
            "username",
            "role",
            "action",
            "object_type",
            "object_id",
            "metadata",
            "ip_address",
        ]
