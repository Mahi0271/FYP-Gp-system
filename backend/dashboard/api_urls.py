from django.urls import path
from .api_views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]