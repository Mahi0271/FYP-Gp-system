from urllib import response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Appointment
from .serializers import AppointmentSerializer
from django.utils import timezone
from django.utils.dateparse import parse_date
from audits.utils import log_event



class AppointmentListCreateView(generics.ListCreateAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        u = self.request.user

        # Base queryset by role
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

        # Optional filters (mostly for staff "manager/receptionist views")
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

        # Staff-only filters
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

        # PATIENT: always force patient=request.user
        if u.role == "PATIENT":
            gp_user = None

        # auto-assign gp from patient_profile.assigned_gp (GPProfile -> user)
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

        # STAFF: can create for anyone (uses patient/gp from request body)
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

    # GP (or anything else): blocked
        raise PermissionDenied("You are not allowed to create appointments.")
    
    

class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        u = self.request.user

        # Staff can access any
        if u.is_superuser or u.role in ["RECEPTIONIST", "PRACTICE_MANAGER"]:
            return obj

        # GP can only access their appointments
        if u.role == "GP" and obj.gp_id == u.id:
            return obj

        # Patient can only access their appointments
        if u.role == "PATIENT" and obj.patient_id == u.id:
            return obj

        raise PermissionDenied("You do not have access to this appointment.")

    def update(self, request, *args, **kwargs):
    
    #Strip patient/gp BEFORE serializer validation so Swagger can't break PATCH/PUT
    #with invalid pk values.
    
        u = request.user

        if u.role in ["PATIENT", "GP"]:
            data = request.data.copy()
            data.pop("patient", None)
            data.pop("gp", None)
            request._full_data = data  # ensures DRF uses the modified data

        response = super().update(request, *args, **kwargs)

    # After successful update (PATCH/PUT)
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

       


        
    
