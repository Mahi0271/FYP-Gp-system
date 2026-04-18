"""
URL patterns for the dashboard API (mounted at /api/dashboard/).

  GET /api/dashboard/  → Aggregated metrics for the practice manager.
                         Optional: ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
"""
from django.urls import path
from .api_views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]