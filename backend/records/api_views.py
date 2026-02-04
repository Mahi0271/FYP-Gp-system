from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from audits.utils import log_event



from accounts.models import User
from .models import MedicalRecord, ClinicalEntry
from .serializers import MedicalRecordSerializer, ClinicalEntrySerializer, gp_is_assigned_to_patient


def can_read_record(user: User, record: MedicalRecord) -> bool:
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.role == User.Role.PATIENT:
        return record.patient_id == user.id

    if user.role == User.Role.GP:
        return gp_is_assigned_to_patient(user, record.patient)

    return False  # receptionist/manager denied


class MedicalRecordListView(generics.ListAPIView):
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        u: User = self.request.user

        if u.is_superuser:
            return MedicalRecord.objects.all()

        if u.role == User.Role.PATIENT:
            return MedicalRecord.objects.filter(patient=u)

        if u.role == User.Role.GP:
            # Records for patients assigned to this GP
            return MedicalRecord.objects.filter(patient__patient_profile__assigned_gp__user=u)

        # Staff cannot view records list
        raise PermissionDenied("You do not have access to medical records.")


class MedicalRecordMeView(generics.RetrieveAPIView):
    serializer_class = MedicalRecordSerializer

    def get_object(self):
        u: User = self.request.user
        if u.role != User.Role.PATIENT:
            raise PermissionDenied("Only patients can use this endpoint.")
        try:
            return u.medical_record
        except MedicalRecord.DoesNotExist:
            # Should not happen if signals work, but safe fallback
            return MedicalRecord.objects.create(patient=u)


class MedicalRecordDetailView(generics.RetrieveAPIView):
    serializer_class = MedicalRecordSerializer
    queryset = MedicalRecord.objects.select_related("patient")

    def get_object(self):
        record = super().get_object()
        if not can_read_record(self.request.user, record):
            raise PermissionDenied("You do not have access to this record.")
        return record


class RecordEntriesListCreateView(generics.ListCreateAPIView):
    serializer_class = ClinicalEntrySerializer

    def get_record(self) -> MedicalRecord:
        try:
            record = MedicalRecord.objects.select_related("patient").get(pk=self.kwargs["record_id"])
        except MedicalRecord.DoesNotExist:
            raise NotFound("Medical record not found.")

        if not can_read_record(self.request.user, record):
            raise PermissionDenied("You do not have access to this record.")
        return record


    def get_queryset(self):
        record = self.get_record()
        return ClinicalEntry.objects.filter(record=record).select_related("created_by")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["record"] = self.get_record()
        return ctx
    
    def perform_create(self, serializer):
        entry = serializer.save()
        log_event(
            self.request,
            action="RECORD_ENTRY_CREATE",
            obj=entry,
            object_type="clinical_entry",
            metadata={
                "record_id": entry.record_id,
                "patient_id": entry.record.patient_id,
                "type": entry.type,
            },
        )



class ClinicalEntryDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ClinicalEntrySerializer
    queryset = ClinicalEntry.objects.select_related("record", "record__patient", "created_by")

    def get_object(self):
        entry = super().get_object()
        record = entry.record
        if not can_read_record(self.request.user, record):
            raise PermissionDenied("You do not have access to this record.")
        return entry

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        entry = self.get_object()
        ctx["record"] = entry.record
        return ctx
    
    def perform_update(self, serializer):
        entry = serializer.save()
        log_event(
            self.request,
            action="RECORD_ENTRY_UPDATE",
            obj=entry,
            object_type="clinical_entry",
            metadata={
                "record_id": entry.record_id,
                "patient_id": entry.record.patient_id,
                "type": entry.type,
            },
        )

