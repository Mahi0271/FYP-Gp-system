from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


from accounts.models import User
from .models import AuditLog
from .serializers import AuditLogSerializer



@extend_schema(
    parameters=[
        OpenApiParameter(
            name="date_from",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter: include logs from this date (YYYY-MM-DD)."
        ),
        OpenApiParameter(
            name="date_to",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter: include logs up to this date (YYYY-MM-DD)."
        ),
        OpenApiParameter(
            name="user",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by user id."
        ),
        OpenApiParameter(
            name="action",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by action string (e.g. APPOINTMENT_CREATE, APPOINTMENT_UPDATE, RECORD_ENTRY_CREATE)."
        ),
        OpenApiParameter(
            name="object_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter by object type (e.g. appointment, record_entry)."
        ),
    ],
    description="Manager-only. Lists audit logs. Supports filtering by date range, user, action, and object_type.",
)


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        u: User = self.request.user

        # Manager only (and allow superuser)
        if not (u.is_authenticated and (u.is_superuser or u.role == User.Role.PRACTICE_MANAGER)):
            raise PermissionDenied("Only practice managers can view audit logs.")

        qs = AuditLog.objects.select_related("user").all()
        params = self.request.query_params

        # Filters
        date_from = params.get("date_from")
        if date_from:
            d = parse_date(date_from)
            if not d:
                raise ValidationError({"date_from": "Invalid date. Use YYYY-MM-DD."})
            qs = qs.filter(timestamp__date__gte=d)

        date_to = params.get("date_to")
        if date_to:
            d = parse_date(date_to)
            if not d:
                raise ValidationError({"date_to": "Invalid date. Use YYYY-MM-DD."})
            qs = qs.filter(timestamp__date__lte=d)

        user_id = params.get("user")
        if user_id:
            try:
                qs = qs.filter(user_id=int(user_id))
            except (TypeError, ValueError):
                raise ValidationError({"user": "Invalid user id."})

        action = params.get("action")
        if action:
            qs = qs.filter(action=action)

        object_type = params.get("object_type")
        if object_type:
            qs = qs.filter(object_type=object_type)

        return qs
