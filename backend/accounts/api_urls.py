"""
URL patterns for the accounts API (mounted at /api/accounts/ in urls.py).

Endpoint summary:
  GET  me/                           → Returns the logged-in user's id, role, and MFA status
  POST signup/                       → Public patient self-registration (no auth required)
  POST logout/                       → Blacklists the refresh token so it can't be reused
  PATCH patients/<id>/contact/       → Receptionist updates a patient's contact details

  MFA (time-based one-time passwords via Google Authenticator etc.):
    POST mfa/setup/                  → Generates a new TOTP secret and QR code URL
    POST mfa/enable/                 → Activates MFA after the user verifies their first code
    POST mfa/disable/                → Turns off MFA (requires a valid code to confirm)
    POST mfa/verify/                 → Login endpoint for MFA users: username+password+code → JWT

  Password reset (two-step flow):
    POST password-reset/             → Step 1: request a reset token for an email address
    POST password-reset/confirm/     → Step 2: submit the token and new password
"""
from django.urls import path
from . import api_views

urlpatterns = [
    path("me/", api_views.MeView.as_view(), name="me"),
    path("signup/", api_views.PatientSignupView.as_view(), name="patient_signup"),
    path("logout/", api_views.LogoutView.as_view(), name="logout"),

    path("patients/<int:patient_id>/contact/", api_views.ReceptionistUpdatePatientContactView.as_view(), name="patient_contact_update"),

    # MFA (TOTP) — Multi-Factor Authentication using a time-based one-time password
    path("mfa/setup/", api_views.MFASetupView.as_view(), name="mfa_setup"),
    path("mfa/enable/", api_views.MFAEnableView.as_view(), name="mfa_enable"),
    path("mfa/disable/", api_views.MFADisableView.as_view(), name="mfa_disable"),
    path("mfa/verify/", api_views.MFAVerifyLoginView.as_view(), name="mfa_verify_login"),

    # Password reset — two-step: request token, then submit token + new password
    path("password-reset/", api_views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", api_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]