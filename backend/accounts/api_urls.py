from django.urls import path
from . import api_views

urlpatterns = [
    path("me/", api_views.MeView.as_view(), name="me"),
    path("signup/", api_views.PatientSignupView.as_view(), name="patient_signup"),
    path("logout/", api_views.LogoutView.as_view(), name="logout"),

    path("patients/<int:patient_id>/contact/", api_views.ReceptionistUpdatePatientContactView.as_view(), name="patient_contact_update"),

    # MFA (TOTP)
    path("mfa/setup/", api_views.MFASetupView.as_view(), name="mfa_setup"),
    path("mfa/enable/", api_views.MFAEnableView.as_view(), name="mfa_enable"),
    path("mfa/disable/", api_views.MFADisableView.as_view(), name="mfa_disable"),
    path("mfa/verify/", api_views.MFAVerifyLoginView.as_view(), name="mfa_verify_login"),

    # Password reset
    path("password-reset/", api_views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password-reset/confirm/", api_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]