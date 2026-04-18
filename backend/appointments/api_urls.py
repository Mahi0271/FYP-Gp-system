"""
URL patterns for the appointments API (mounted at /api/appointments/).

  GET/POST   /api/appointments/                → List all appointments (filtered by role) or create one
  GET        /api/appointments/availability/   → Show free 15-min slots for a given GP and date
  GET/PATCH  /api/appointments/<id>/           → View or update a single appointment
"""
from django.urls import path
from . import api_views
from .availability import AvailabilityView

urlpatterns = [
    path("", api_views.AppointmentListCreateView.as_view(), name="appointment_list_create"),
    path("availability/", AvailabilityView.as_view(), name="appointment_availability"),
    path("<int:pk>/", api_views.AppointmentDetailView.as_view(), name="appointment_detail"),
]
