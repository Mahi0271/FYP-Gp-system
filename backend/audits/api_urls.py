"""
URL patterns for the audits API (mounted at /api/audits/).

  GET /api/audits/  → Paginated list of audit log entries (practice managers only).
                      Supports ?date_from, ?date_to, ?user, ?action, ?object_type filters.
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path("", api_views.AuditLogListView.as_view(), name="audit_list"),
]
