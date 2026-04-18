"""
Dashboard API view — aggregated metrics for the practice manager.

Returns a single JSON payload summarising activity across all parts of
the system for a given date range (defaulting to the last 7 days):

  appointments  → total, breakdown by status, upcoming count
  records       → total number of medical records
  entries       → new clinical entries written in the date range
  audits        → total audit events + the 5 most frequent action types

Only practice managers and superusers can access this endpoint.
"""
from datetime import datetime, time
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from accounts.models import User
from appointments.models import Appointment
from records.models import MedicalRecord, ClinicalEntry
from audits.models import AuditLog


def _day_start(d):
    """Convert a date to a timezone-aware datetime at midnight (start of day)."""
    return timezone.make_aware(datetime.combine(d, time.min))


def _day_end_exclusive(d):
    """
    Return the start of the *next* day so date-range filters are end-exclusive.
    e.g. date_to=2024-01-07 → end at 2024-01-08 00:00 to include all of the 7th.
    """
    return timezone.make_aware(datetime.combine(d, time.min)) + timezone.timedelta(days=1)


class DashboardView(APIView):
    """
    Manager-only dashboard metrics.
    Optional query params:
      - date_from=YYYY-MM-DD
      - date_to=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
    description="Manager-only dashboard metrics. Optional query params: date_from, date_to (YYYY-MM-DD).",
    parameters=[
        OpenApiParameter(
            name="date_from",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Start date (YYYY-MM-DD). Defaults to last 7 days.",
        ),
        OpenApiParameter(
            name="date_to",
            type=OpenApiTypes.DATE,
            location=OpenApiParameter.QUERY,
            required=False,
            description="End date (YYYY-MM-DD). Defaults to today.",
        ),
    ],
)

    def get(self, request):
        u: User = request.user

        # Manager-only (superuser allowed)
        if not (u.is_superuser or u.role == User.Role.PRACTICE_MANAGER):
            raise PermissionDenied("Only practice managers can view the dashboard.")

        params = request.query_params
        date_from = params.get("date_from")
        date_to = params.get("date_to")

        # Default range: last 7 days (including today)
        today = timezone.now().date()
        df = today - timezone.timedelta(days=6)
        dt = today

        if date_from:
            parsed = parse_date(date_from)
            if not parsed:
                raise ValidationError({"date_from": "Invalid date. Use YYYY-MM-DD."})
            df = parsed

        if date_to:
            parsed = parse_date(date_to)
            if not parsed:
                raise ValidationError({"date_to": "Invalid date. Use YYYY-MM-DD."})
            dt = parsed

        if df > dt:
            raise ValidationError({"date_range": "date_from must be <= date_to."})

        start_dt = _day_start(df)
        end_dt = _day_end_exclusive(dt)

        # Appointments in range (by start_time)
        appt_qs = Appointment.objects.filter(start_time__gte=start_dt, start_time__lt=end_dt)

        appt_total = appt_qs.count()
        appt_by_status = dict(
            appt_qs.values("status").annotate(c=Count("id")).values_list("status", "c")
        )

        # Upcoming appointments (from now) - all roles view, but dashboard is manager-only anyway
        upcoming_count = Appointment.objects.filter(start_time__gte=timezone.now()).count()

        # Records
        records_total = MedicalRecord.objects.count()

        # Entries created in range (by created_at)
        entries_in_range = ClinicalEntry.objects.filter(created_at__gte=start_dt, created_at__lt=end_dt).count()

        # Audits in range (by timestamp)
        audit_qs = AuditLog.objects.filter(timestamp__gte=start_dt, timestamp__lt=end_dt)
        audits_total = audit_qs.count()

        top_actions = list(
            audit_qs.values("action")
            .exclude(action="")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )

        payload = {
            "range": {"date_from": str(df), "date_to": str(dt)},
            "appointments": {
                "total_in_range": appt_total,
                "by_status_in_range": appt_by_status,
                "upcoming_total": upcoming_count,
            },
            "records": {"total": records_total},
            "entries": {"created_in_range": entries_in_range},
            "audits": {
                "total_in_range": audits_total,
                "top_actions": top_actions,
            },
        }

        return Response(payload)