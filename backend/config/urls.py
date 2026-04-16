from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .frontend_views import serve_frontend


urlpatterns = [
    path("admin/", admin.site.urls),

    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # App APIs
    path("api/accounts/",     include("accounts.api_urls")),
    path("api/appointments/", include("appointments.api_urls")),
    path("api/records/",      include("records.api_urls")),
    path("api/audits/",       include("audits.api_urls")),
    path("api/dashboard/",    include("dashboard.api_urls")),

    # Frontend — served at root; must be last so API routes take priority
    re_path(r"^$",              serve_frontend, {"path": "index.html"}),
    re_path(r"^(?P<path>.+)$",  serve_frontend),
]
