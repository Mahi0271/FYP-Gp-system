"""
Serializers for medical records and clinical entries.

Key design decisions:
  - MedicalRecordSerializer is read-only (no create/update in the API).
  - ClinicalEntrySerializer handles the encrypt/decrypt cycle for content:
      * On write (create/update): takes plaintext from the request, calls
        PostgreSQL's pgp_sym_encrypt() via a raw UPDATE query, and clears
        the plaintext 'content' column to ''.
      * On read: the view annotates the queryset with pgp_sym_decrypt() as
        'content_plain', and to_representation() surfaces it as 'content'.
  - Role-based write rules are enforced in validate():
      * Patients → read-only (ValidationError on any create/update attempt)
      * Staff (Receptionist, Manager) → no access
      * GPs → can only write for their own assigned patients

gp_is_assigned_to_patient() is a shared helper imported by api_views.py too.
"""
from rest_framework import serializers
from accounts.models import User
from .models import MedicalRecord, ClinicalEntry
from django.conf import settings
from django.db import connection


def gp_is_assigned_to_patient(gp_user: User, patient_user: User) -> bool:
    """
    Check whether a GP user is assigned to a specific patient.

    Returns False on any exception (missing profile, None assigned_gp, etc.)
    so callers can treat it as a simple boolean without try/except blocks.
    """
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

    # populated by api_views.py annotate(content_plain=...)
    content_plain = serializers.CharField(read_only=True)

    class Meta:
        model = ClinicalEntry
        fields = [
            "id",
            "record",
            "type",
            "title",
            "content",        # write input
            "content_plain",  # read output (decrypted)
            "created_by_id",
            "created_by_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["record", "created_by_id", "created_by_username", "created_at", "updated_at"]

    def to_representation(self, instance):
        """
        Return decrypted content as 'content' so the API stays the same.
        """
        data = super().to_representation(instance)
        data["content"] = data.get("content_plain") or ""
        data.pop("content_plain", None)
        return data

    def _encrypt_content(self, entry_id: int, plaintext: str) -> None:
        """
        Store encrypted content in content_enc (bytea) using pgcrypto,
        and clear plaintext content column.

        IMPORTANT: explicit casts avoid pgcrypto "unknown, unknown" signature errors,
        especially in tests.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE records_clinicalentry
                SET content_enc = pgp_sym_encrypt(%s::text, %s::text),
                    content = ''
                WHERE id = %s
                """,
                [plaintext, settings.PGCRYPTO_KEY, entry_id],
            )

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

        # take plaintext from request but DO NOT store it in DB plaintext column
        plaintext = validated_data.pop("content", "")

        entry = ClinicalEntry.objects.create(
            record=record,
            created_by=request.user,
            content="",  # never store plaintext
            **validated_data,
        )

        self._encrypt_content(entry.id, plaintext)
        return entry

    def update(self, instance, validated_data):
        plaintext = validated_data.pop("content", None)

        # update other fields normally
        for k, v in validated_data.items():
            setattr(instance, k, v)

        # ensure plaintext content stays empty
        instance.content = ""
        instance.save()

        # if content was provided, update encrypted column
        if plaintext is not None:
            self._encrypt_content(instance.id, plaintext)

        return instance