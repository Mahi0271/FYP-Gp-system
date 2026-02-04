from django.urls import path
from . import api_views

urlpatterns = [
    path("", api_views.AuditLogListView.as_view(), name="audit_list"),
]
