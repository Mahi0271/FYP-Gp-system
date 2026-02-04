
from django.urls import path
from . import api_views
from .availability import AvailabilityView

urlpatterns = [
    path("", api_views.AppointmentListCreateView.as_view(), name="appointment_list_create"),
    path("availability/", AvailabilityView.as_view(), name="appointment_availability"),
    path("<int:pk>/", api_views.AppointmentDetailView.as_view(), name="appointment_detail"),
]
