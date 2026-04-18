"""
Master URL configuration for the GP Secure System.

How routing works:
  - /admin/          → Django's built-in admin panel
  - /api/schema/     → Raw OpenAPI JSON schema (used by the docs UI)
  - /api/docs/       → Interactive Swagger UI — great for exploring the API
  - /api/token/      → Log in with username+password, get JWT access+refresh tokens
  - /api/token/refresh/ → Exchange a refresh token for a new access token
  - /api/accounts/   → User management: signup, MFA, logout, password reset
  - /api/appointments/ → Appointment booking and management
  - /api/records/    → Medical records and clinical entries
  - /api/audits/     → Audit log viewer (practice managers only)
  - /api/dashboard/  → Summary metrics (practice managers only)
  - Everything else  → Served as a static frontend file (HTML/CSS/JS)

The frontend catch-all pattern must be last so API routes always win.
"""
from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .frontend_views import serve_frontend


urlpatterns = [
    path("admin/", admin.site.urls),

    # API docs — visit /api/docs/ in your browser to explore every endpoint
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # Standard JWT login: POST {username, password} → {access, refresh}
    # Use /api/accounts/mfa/verify/ instead when MFA is enabled
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Each app registers its own URL patterns in its api_urls.py file
    path("api/accounts/",     include("accounts.api_urls")),
    path("api/appointments/", include("appointments.api_urls")),
    path("api/records/",      include("records.api_urls")),
    path("api/audits/",       include("audits.api_urls")),
    path("api/dashboard/",    include("dashboard.api_urls")),

    # Catch-all: serve the vanilla JS frontend from backend/frontend/
    # Must be last — any unmatched URL is assumed to be a frontend page
    re_path(r"^$",              serve_frontend, {"path": "index.html"}),
    re_path(r"^(?P<path>.+)$",  serve_frontend),
]
