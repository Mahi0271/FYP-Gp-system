from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
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
