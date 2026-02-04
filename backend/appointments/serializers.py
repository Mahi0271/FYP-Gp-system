from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment

User = get_user_model()


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="PATIENT"),
        required=False,
    )
    gp = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="GP"),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Appointment
        fields = [
            "id", "patient", "gp",
            "start_time", "end_time",
            "status", "reason", "created_at",
        ]
        read_only_fields = ["id", "created_at"]  # NOTE: don't make patient/gp read-only globally

    def _get_patient_assigned_gp_user(self, user):
        """
        For PATIENT users, infer assigned GP (User) from patient_profile.assigned_gp.user.
        Returns None if no assigned GP.
        """
        if not user:
            return None
        if hasattr(user, "patient_profile") and getattr(user.patient_profile, "assigned_gp", None):
            return user.patient_profile.assigned_gp.user
        return None

    def validate(self, attrs):
        """
        - Basic time validation
        - GP double booking prevention
        - Role-based status transitions (PATCH)
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        instance = getattr(self, "instance", None)

                # ----- ROLE-BASED UPDATE FIELD RULES -----
        # Default rules:
        # - PATIENT: may only update status (cancel)
        # - GP: may only update status (complete)
        # - Staff: may update fields as needed
        if instance is not None and user is not None:
            if user.role == "PATIENT":
                forbidden = set(attrs.keys()) - {"status"}
                if forbidden:
                    raise serializers.ValidationError({
                        "detail": "Patients may only cancel appointments (status only)."
                    })
            elif user.role == "GP":
                forbidden = set(attrs.keys()) - {"status"}
                if forbidden:
                    raise serializers.ValidationError({
                        "detail": "GPs may only complete appointments (status only)."
                    })

        # ----- TIME VALIDATION -----
        start_time = attrs.get("start_time", getattr(instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(instance, "end_time", None))

        changing_times = (
            instance is None
            or ("start_time" in attrs)
            or ("end_time" in attrs)
        )

        if changing_times and start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({"end_time": "end_time must be after start_time."})

        # Optional: block booking in the past (uncomment if you want)
        # if start_time and start_time < timezone.now():
        #     raise serializers.ValidationError({"start_time": "start_time cannot be in the past."})

        # ----- STATUS TRANSITION RULES -----
        new_status = attrs.get("status", None)
        old_status = getattr(instance, "status", None)

        if instance is not None and new_status is not None and user is not None:
            if user.role == "PATIENT":
                if new_status != Appointment.Status.CANCELLED:
                    raise serializers.ValidationError({"status": "Patients can only cancel appointments."})

            elif user.role == "GP":
                allowed = {Appointment.Status.COMPLETED}
                # If you want GP to cancel too:
                # allowed = {Appointment.Status.COMPLETED, Appointment.Status.CANCELLED}
                if new_status not in allowed:
                    raise serializers.ValidationError({"status": "GP can only complete appointments."})

            elif user.is_superuser or user.role in ["RECEPTIONIST", "PRACTICE_MANAGER"]:
                allowed = {
                    Appointment.Status.CONFIRMED,
                    Appointment.Status.CANCELLED,
                    Appointment.Status.REQUESTED,  # optional
                    Appointment.Status.COMPLETED,  # optional
                }
                if new_status not in allowed:
                    raise serializers.ValidationError({"status": "Invalid status for staff role."})

        if instance is not None and new_status is not None:
            if old_status == Appointment.Status.COMPLETED and new_status != Appointment.Status.COMPLETED:
                raise serializers.ValidationError({"status": "Completed appointments cannot be changed."})

        # ----- GP OVERLAP VALIDATION -----
        # IMPORTANT FIX:
        # If PATIENT is creating and didn't send "gp", infer the assigned GP now (before overlap check).
        if instance is None and user is not None and user.role == "PATIENT" and "gp" not in attrs:
            inferred_gp = self._get_patient_assigned_gp_user(user)
            if inferred_gp is not None:
                attrs["gp"] = inferred_gp

        changing_slot = (
            instance is None
            or ("start_time" in attrs)
            or ("end_time" in attrs)
            or ("gp" in attrs)
        )

        gp = attrs.get("gp", getattr(instance, "gp", None))

        # Only check overlap if we have gp + times
        if changing_slot and gp and start_time and end_time:
            qs = Appointment.objects.filter(gp=gp)

            # Optional: ignore cancelled appointments for conflict checks
            qs = qs.exclude(status=Appointment.Status.CANCELLED)

            if instance is not None:
                qs = qs.exclude(pk=instance.pk)

            conflict = qs.filter(start_time__lt=end_time, end_time__gt=start_time).exists()
            if conflict:
                raise serializers.ValidationError({"gp": "This GP already has an appointment in that time range."})

        return attrs

    def update(self, instance, validated_data):
        """
        Prevent patients from changing patient/gp via PATCH even if they send it.
        Staff can change.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if user and user.role == "PATIENT":
            validated_data.pop("patient", None)
            validated_data.pop("gp", None)

        return super().update(instance, validated_data)
