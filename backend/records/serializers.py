from rest_framework import serializers
from accounts.models import User
from .models import MedicalRecord, ClinicalEntry


def gp_is_assigned_to_patient(gp_user: User, patient_user: User) -> bool:
    try:
        return (
            gp_user.role == User.Role.GP
            and patient_user.patient_profile.assigned_gp is not None
            and patient_user.patient_profile.assigned_gp.user_id == gp_user.id
        )
    except Exception:
        return False


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    patient_username = serializers.CharField(source="patient.username", read_only=True)

    class Meta:
        model = MedicalRecord
        fields = ["id", "patient_id", "patient_username", "created_at", "updated_at"]


class ClinicalEntrySerializer(serializers.ModelSerializer):
    created_by_id = serializers.IntegerField(source="created_by.id", read_only=True)
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = ClinicalEntry
        fields = [
            "id",
            "record",
            "type",
            "title",
            "content",
            "created_by_id",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["record", "created_by_id", "created_by_username", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return attrs

        user: User = request.user
        record: MedicalRecord = self.context.get("record")

        # Patient read-only (no create/update)
        if user.role == User.Role.PATIENT:
            raise serializers.ValidationError({"detail": "Patients have read-only access to records."})

        # Staff have no access
        if user.role in [User.Role.RECEPTIONIST, User.Role.PRACTICE_MANAGER]:
            raise serializers.ValidationError({"detail": "Staff cannot modify medical records."})

        # GP can write only for assigned patients
        if user.role == User.Role.GP:
            if not gp_is_assigned_to_patient(user, record.patient):
                raise serializers.ValidationError({"detail": "You are not assigned to this patient."})

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        record: MedicalRecord = self.context["record"]
        return ClinicalEntry.objects.create(
            record=record,
            created_by=request.user,
            **validated_data,
        )
