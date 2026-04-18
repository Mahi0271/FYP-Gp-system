"""
API views for listing, creating, and updating appointments.

Access rules enforced here:
  - Patients see only their own appointments.
  - GPs see only appointments where they are the assigned doctor.
  - Receptionists and Practice Managers see all appointments.

Both views write to the audit log on create/update so there is a permanent
record of who changed what and when.
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_date

from audits.utils import log_event
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    GET  → returns a list of appointments visible to the current user.
    POST → creates a new appointment.

    Supported query parameters for filtering:
      upcoming=1         → only future appointments
      date_from=YYYY-MM-DD / date_to=YYYY-MM-DD → date range
      patient=<id>       → staff-only filter by patient
      gp=<id>            → staff-only filter by GP
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user

        if u.is_superuser or u.role in ["RECEPTIONIST", "PRACTICE_MANAGER"]:
            qs = Appointment.objects.all()
            staff = True
        elif u.role == "GP":
            qs = Appointment.objects.filter(gp=u)
            staff = False
        elif u.role == "PATIENT":
            qs = Appointment.objects.filter(patient=u)
            staff = False
        else:
            qs = Appointment.objects.none()
            staff = False

        params = self.request.query_params

        upcoming = params.get("upcoming")
        if str(upcoming).lower() in {"1", "true", "yes", "y", "on"}:
            qs = qs.filter(start_time__gte=timezone.now())

        date_from = params.get("date_from")
        if date_from:
            d = parse_date(date_from)
            if not d:
                raise ValidationError({"date_from": "Invalid date. Use YYYY-MM-DD."})
            qs = qs.filter(start_time__date__gte=d)

        date_to = params.get("date_to")
        if date_to:
            d = parse_date(date_to)
            if not d:
                raise ValidationError({"date_to": "Invalid date. Use YYYY-MM-DD."})
            qs = qs.filter(start_time__date__lte=d)

        if staff:
            patient = params.get("patient")
            if patient:
                try:
                    qs = qs.filter(patient_id=int(patient))
                except (TypeError, ValueError):
                    raise ValidationError({"patient": "Invalid patient id."})

            gp = params.get("gp")
            if gp:
                try:
                    qs = qs.filter(gp_id=int(gp))
                except (TypeError, ValueError):
                    raise ValidationError({"gp": "Invalid gp id."})

        return qs.order_by("-start_time")

    def perform_create(self, serializer):
        u = self.request.user

        if u.role == "PATIENT":
            gp_user = None

            if hasattr(u, "patient_profile") and u.patient_profile.assigned_gp:
                gp_user = u.patient_profile.assigned_gp.user

            appt = serializer.save(patient=u, gp=gp_user)
            log_event(
                self.request,
                action="APPOINTMENT_CREATE",
                obj=appt,
                object_type="appointment",
                metadata={"status": appt.status},
            )
            return

        if u.is_superuser or u.role in ["RECEPTIONIST", "PRACTICE_MANAGER"]:
            appt = serializer.save()
            log_event(
                self.request,
                action="APPOINTMENT_CREATE",
                obj=appt,
                object_type="appointment",
                metadata={"status": appt.status},
            )
            return

        raise PermissionDenied("You are not allowed to create appointments.")


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   → view a single appointment (if you're allowed to see it).
    PATCH → update a single appointment's status or details.

    Permission check in get_object() ensures users can only see appointments
    they are directly involved in (unless they're staff).

    Before passing data to the serializer on PATCH, we strip 'patient' and 'gp'
    from the request body for non-staff users — this prevents a patient from
    reassigning their appointment to a different GP by sending a crafted request.
    """
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        u = self.request.user

        # Staff (receptionist, manager) can view any appointment
        if u.is_superuser or u.role in ["RECEPTIONIST", "PRACTICE_MANAGER"]:
            return obj

        # A GP can only see appointments assigned to them
        if u.role == "GP" and obj.gp_id == u.id:
            return obj

        # A patient can only see their own appointments
        if u.role == "PATIENT" and obj.patient_id == u.id:
            return obj

        raise PermissionDenied("You do not have access to this appointment.")

    def update(self, request, *args, **kwargs):
        u = request.user

        # Patients and GPs cannot change who the appointment belongs to.
        # Strip those fields out before the serializer sees them to avoid 400 errors
        # from the PrimaryKeyRelatedField validation when those IDs don't belong to the user.
        if u.role in ["PATIENT", "GP"]:
            data = request.data.copy()
            data.pop("patient", None)
            data.pop("gp", None)
            request._full_data = data

        response = super().update(request, *args, **kwargs)

        # Log the change only on success
        if response.status_code in (200, 201):
            appt = self.get_object()
            log_event(
                request,
                action="APPOINTMENT_UPDATE",
                obj=appt,
                object_type="appointment",
                metadata={"status": appt.status},
            )

        return response
