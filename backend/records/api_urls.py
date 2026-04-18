"""
URL patterns for the medical records API (mounted at /api/records/).

  GET  /api/records/                    → List medical records visible to the current user
  GET  /api/records/me/                 → Patient shortcut: get your own medical record
  GET  /api/records/<id>/               → View a specific medical record by id
  GET/POST  /api/records/<id>/entries/  → List or add clinical entries on a record
  GET/PATCH /api/records/entries/<id>/  → View or update a single clinical entry
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path("", api_views.MedicalRecordListView.as_view(), name="record_list"),
    path("me/", api_views.MedicalRecordMeView.as_view(), name="record_me"),
    path("<int:pk>/", api_views.MedicalRecordDetailView.as_view(), name="record_detail"),
    path("<int:record_id>/entries/", api_views.RecordEntriesListCreateView.as_view(), name="record_entries"),
    path("entries/<int:pk>/", api_views.ClinicalEntryDetailView.as_view(), name="entry_detail"),
]
