from django.urls import path
from . import api_views

urlpatterns = [
    path("", api_views.MedicalRecordListView.as_view(), name="record_list"),
    path("me/", api_views.MedicalRecordMeView.as_view(), name="record_me"),
    path("<int:pk>/", api_views.MedicalRecordDetailView.as_view(), name="record_detail"),
    path("<int:record_id>/entries/", api_views.RecordEntriesListCreateView.as_view(), name="record_entries"),
    path("entries/<int:pk>/", api_views.ClinicalEntryDetailView.as_view(), name="entry_detail"),
]
