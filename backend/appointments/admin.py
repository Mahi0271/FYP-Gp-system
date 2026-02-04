from django.contrib import admin
from django.db.models import Q

from accounts.models import User, PatientProfile
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "gp", "start_time", "end_time", "status")
    list_filter = ("status", "start_time", "gp")
    search_fields = ("patient__username", "gp__username", "reason")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs

        # Receptionist + Practice Manager can view all
        if user.role in {User.Role.RECEPTIONIST, User.Role.PRACTICE_MANAGER}:
            return qs

        # GP: only appointments for patients assigned to them
        if user.role == User.Role.GP:
            return qs.filter(gp=user)

        # Patient: only their own appointments
        if user.role == User.Role.PATIENT:
            return qs.filter(patient=user)

        # Default: nothing
        return qs.none()

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser:
            return True
        if obj is None:
            return True  # allow loading list page, add page etc.

        if user.role in {User.Role.RECEPTIONIST, User.Role.PRACTICE_MANAGER}:
            return True

        if user.role == User.Role.GP:
            return obj.patient.patient_profile.assigned_gp and obj.patient.patient_profile.assigned_gp.user_id == user.id

        if user.role == User.Role.PATIENT:
            return obj.patient_id == user.id

        return False

    def has_delete_permission(self, request, obj=None):
        # Let receptionist/manager delete if needed; keep patients/GP from deleting by admin
        user = request.user
        if user.is_superuser:
            return True
        if user.role in {User.Role.RECEPTIONIST, User.Role.PRACTICE_MANAGER}:
            return True
        return False

    def save_model(self, request, obj, form, change):
        """
        Safety: if a PATIENT creates an appointment in admin,
        force patient = themselves and gp = assigned GP (if exists).
        """
        user = request.user

        if not user.is_superuser and user.role == User.Role.PATIENT:
            obj.patient = user
            # auto-attach assigned GP if available
            try:
                assigned = user.patient_profile.assigned_gp
                obj.gp = assigned.user if assigned else None
            except PatientProfile.DoesNotExist:
                obj.gp = None

        super().save_model(request, obj, form, change)
