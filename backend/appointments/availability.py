# backend/appointments/availability.py

from datetime import datetime, time, timedelta, timezone as dt_timezone
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


from .models import Appointment

User = get_user_model()


class AvailabilityView(APIView):
    """
    GET /api/appointments/availability/?date=YYYY-MM-DD&gp=<gp_id>

    Returns available 15-min slots between 09:00–17:00 UTC (exclusive end).
    Removes any slot that overlaps existing appointments for that GP.
    """
    permission_classes = [IsAuthenticated]

    SLOT_MINUTES = 15
    DAY_START_HOUR = 9
    DAY_END_HOUR = 17

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Required. Date in YYYY-MM-DD format."
            ),
            OpenApiParameter(
                name="gp",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Required. GP user id."
            ),
        ],
        description="Returns available 15-min slots between 09:00–17:00 UTC (exclusive end). Excludes slots overlapping existing appointments for the selected GP.",
        responses={200: OpenApiTypes.OBJECT},
    )
    
    def get(self, request):
        date_str = request.query_params.get("date")
        gp_str = request.query_params.get("gp")

        if not date_str:
            raise ValidationError({"date": "This query param is required (YYYY-MM-DD)."})
        if not gp_str:
            raise ValidationError({"gp": "This query param is required (gp user id)."})


        # Parse date
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError({"date": "Invalid date format. Use YYYY-MM-DD."})

        # Parse gp id
        try:
            gp_id = int(gp_str)
        except ValueError:
            raise ValidationError({"gp": "gp must be an integer user id."})

        # Fetch GP user
        gp_user = User.objects.filter(id=gp_id, role="GP").first()
        if not gp_user:
            raise ValidationError({"gp": "GP user not found."})

        # Role rule: GP can only query their own availability; staff/patient can query any GP
        u = request.user
        if getattr(u, "role", None) == "GP" and u.id != gp_user.id:
            raise PermissionDenied("GPs can only view their own availability.")

        # Build day window in UTC
        window_start = datetime.combine(day, time(self.DAY_START_HOUR, 0, 0)).replace(tzinfo=dt_timezone.utc)
        window_end = datetime.combine(day, time(self.DAY_END_HOUR, 0, 0)).replace(tzinfo=dt_timezone.utc)

        slot_delta = timedelta(minutes=self.SLOT_MINUTES)

        # Grab existing appointments that overlap the day window
        busy_qs = (
            Appointment.objects
            .filter(gp=gp_user, start_time__lt=window_end, end_time__gt=window_start)
            .exclude(status=Appointment.Status.CANCELLED)
            .values_list("start_time", "end_time")
        )
        busy_intervals = list(busy_qs)

        def overlaps(a_start, a_end, b_start, b_end) -> bool:
            # overlap if a_start < b_end AND a_end > b_start
            return a_start < b_end and a_end > b_start

        slots = []
        cur = window_start
        while cur + slot_delta <= window_end:
            slot_start = cur
            slot_end = cur + slot_delta

            conflict = any(
                overlaps(slot_start, slot_end, busy_start, busy_end)
                for (busy_start, busy_end) in busy_intervals
            )

            if not conflict:
                slots.append({
                    "start_time": slot_start.isoformat().replace("+00:00", "Z"),
                    "end_time": slot_end.isoformat().replace("+00:00", "Z"),
                })

            cur += slot_delta

        return Response({
            "date": date_str,
            "gp": gp_user.id,
            "slot_minutes": self.SLOT_MINUTES,
            "window_utc": {
                "start": window_start.isoformat().replace("+00:00", "Z"),
                "end": window_end.isoformat().replace("+00:00", "Z"),
            },
            "available": slots
        })
