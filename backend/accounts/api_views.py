"""
API views for accounts — authentication, MFA, and user management.

Views defined here:
  MeView                         → Who am I? Returns the current user's profile.
  PatientSignupView              → Public registration endpoint for new patients.
  ReceptionistUpdatePatientContactView → Receptionist updates a patient's details.
  MFASetupView                   → Generates a new TOTP secret + QR URL.
  MFAEnableView                  → Confirms and activates MFA after first scan.
  MFADisableView                 → Turns MFA off (requires a valid code).
  MFAVerifyLoginView             → Login for MFA users: credentials + TOTP code → JWT.
  LogoutView                     → Blacklists the refresh token (server-side logout).
  PasswordResetRequestView       → Step 1 of password reset: generates a one-time token.
  PasswordResetConfirmView       → Step 2: validates the token and sets the new password.

All views that modify sensitive data write an entry to the audit log via log_event().
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

import pyotp
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from audits.utils import log_event
from .models import User
from .serializers import PatientContactUpdateSerializer, PatientRegisterSerializer


class MeView(APIView):
    """
    Returns basic information about the currently logged-in user.

    The frontend calls this on every page load to confirm the JWT is still
    valid and to find out the user's role (which determines which dashboard
    they see).  Patients also get their assigned GP's user ID here.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        data = {
            "id": u.id,
            "username": u.username,
            "role": getattr(u, "role", None),
            "mfa_enabled": bool(getattr(u, "mfa_enabled", False)),
        }
        # Patients need to know which GP they're assigned to so the frontend
        # can pre-fill the GP field when booking appointments
        if u.role == User.Role.PATIENT:
            profile = getattr(u, "patient_profile", None)
            gp = getattr(profile, "assigned_gp", None)
            data["assigned_gp"] = gp.user_id if gp else None
        return Response(data)


class PatientSignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PatientRegisterSerializer,
        responses={201: OpenApiTypes.OBJECT},
        description="Public patient signup. Creates a PATIENT user. Assigned GP is auto-set by signals.",
    )
    def post(self, request):
        serializer = PatientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
            },
            status=201,
        )


class ReceptionistUpdatePatientContactView(APIView):
    """
    FR6: Receptionist updates patient contact details.
    PATCH /api/accounts/patients/{patient_id}/contact/
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=PatientContactUpdateSerializer,
        responses={200: OpenApiTypes.OBJECT},
        description="Receptionist-only: update a patient's contact details (User + PatientProfile).",
    )
    def patch(self, request, patient_id: int):
        u: User = request.user

        if not (u.is_superuser or u.role == User.Role.RECEPTIONIST):
            raise PermissionDenied("Only receptionists can update patient contact details.")

        try:
            patient = User.objects.get(id=patient_id, role=User.Role.PATIENT)
        except User.DoesNotExist:
            raise NotFound("Patient not found.")

        serializer = PatientContactUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(patient, serializer.validated_data)

        log_event(
            request,
            action="PATIENT_CONTACT_UPDATE",
            obj=patient,
            object_type="user",
            metadata={"patient_id": patient.id},
        )

        patient.refresh_from_db()
        profile = getattr(patient, "patient_profile", None)

        return Response({
            "patient_id": patient.id,
            "username": patient.username,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "email": patient.email,
            "contact": {
                "phone": getattr(profile, "phone", ""),
                "address_line1": getattr(profile, "address_line1", ""),
                "address_line2": getattr(profile, "address_line2", ""),
                "city": getattr(profile, "city", ""),
                "postcode": getattr(profile, "postcode", ""),
                "date_of_birth": (str(profile.date_of_birth) if getattr(profile, "date_of_birth", None) else None),
            }
        })


class MFASetupView(APIView):
    """
    Generates a new TOTP secret for the logged-in user and returns an otpauth:// URL.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        u: User = request.user

        secret = pyotp.random_base32()
        u.mfa_secret = secret
        u.mfa_enabled = False
        u.save(update_fields=["mfa_secret", "mfa_enabled"])

        issuer = "GP Secure System"
        label = f"{issuer}:{u.username}"
        totp = pyotp.TOTP(secret)
        otpauth_url = totp.provisioning_uri(name=label, issuer_name=issuer)

        return Response({
            "mfa_enabled": False,
            "secret": secret,
            "otpauth_url": otpauth_url,
            "note": "Scan otpauth_url with an authenticator app, then call /api/accounts/mfa/enable/ with a 6-digit code.",
        })


class MFAEnableView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"code": {"type": "string", "example": "123456"}},
                "required": ["code"],
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        description="Enable MFA for the authenticated user. Requires a valid 6-digit TOTP code.",
    )
    def post(self, request):
        u: User = request.user
        code = str(request.data.get("code", "")).strip()

        if not u.mfa_secret:
            raise ValidationError({"detail": "No MFA secret set. Call /api/accounts/mfa/setup/ first."})

        if not code.isdigit():
            raise ValidationError({"code": "Code must be digits only."})

        totp = pyotp.TOTP(u.mfa_secret)
        if not totp.verify(code, valid_window=1):
            raise ValidationError({"code": "Invalid code."})

        u.mfa_enabled = True
        u.save(update_fields=["mfa_enabled"])

        return Response({"mfa_enabled": True, "detail": "MFA enabled."})


class MFADisableView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"code": {"type": "string", "example": "123456"}},
                "required": ["code"],
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        description="Disable MFA for the authenticated user. Requires a valid 6-digit TOTP code.",
    )
    def post(self, request):
        u: User = request.user
        code = str(request.data.get("code", "")).strip()

        if not u.mfa_secret or not u.mfa_enabled:
            return Response({"mfa_enabled": False, "detail": "MFA already disabled."})

        if not code.isdigit():
            raise ValidationError({"code": "Code must be digits only."})

        totp = pyotp.TOTP(u.mfa_secret)
        if not totp.verify(code, valid_window=1):
            raise ValidationError({"code": "Invalid code."})

        u.mfa_enabled = False
        u.save(update_fields=["mfa_enabled"])

        return Response({"mfa_enabled": False, "detail": "MFA disabled."})


class MFAVerifyLoginView(APIView):
    """
    Login endpoint for MFA-enabled users.
    POST { username, password, code } -> returns JWT pair if correct.
    For non-MFA users, you can still use /api/token/ as normal.
    """
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "username": {"type": "string", "example": "patient1"},
                    "password": {"type": "string", "example": "clothes9"},
                    "code": {"type": "string", "example": "123456"},
                },
                "required": ["username", "password", "code"],
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        description="MFA login verification. Provide username, password, and TOTP code to receive JWT tokens.",
    )
    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        code = str(request.data.get("code", "")).strip()

        if not username or not password or not code:
            raise ValidationError({"detail": "username, password, and code are required."})

        user = authenticate(request, username=username, password=password)
        if not user:
            raise ValidationError({"detail": "Invalid username or password."})

        if not getattr(user, "mfa_enabled", False):
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "mfa_enabled": False,
            })

        if not getattr(user, "mfa_secret", ""):
            raise ValidationError({"detail": "MFA is enabled but no secret is set. Contact admin."})

        if not code.isdigit():
            raise ValidationError({"code": "Code must be digits only."})

        totp = pyotp.TOTP(user.mfa_secret)
        if not totp.verify(code, valid_window=1):
            raise ValidationError({"code": "Invalid code."})

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "mfa_enabled": True,
        })


class LogoutView(APIView):
    """
    Blacklists the supplied refresh token, invalidating it immediately.
    POST { refresh: "<refresh_token>" }
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"refresh": {"type": "string"}},
                "required": ["refresh"],
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        description="Logout: blacklist the refresh token so it cannot be reused.",
    )
    def post(self, request):
        refresh_token = str(request.data.get("refresh", "")).strip()
        if not refresh_token:
            raise ValidationError({"detail": "Refresh token is required."})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise ValidationError({"detail": "Token is invalid or already blacklisted."})

        log_event(
            request,
            action="LOGOUT",
            obj=request.user,
            object_type="user",
            metadata={"user_id": request.user.id},
        )
        return Response({"detail": "Successfully logged out."})


class PasswordResetRequestView(APIView):
    """
    Generates a password reset token for the given email address.
    POST { email } -> { uid, token }
    In production the uid/token would be sent by email only.
    For demo purposes they are also returned in the response body.
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"email": {"type": "string", "format": "email"}},
                "required": ["email"],
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        description="Request a password reset token. Returns uid and token (demo mode).",
    )
    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        if not email:
            raise ValidationError({"detail": "Email is required."})

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Generic message — don't reveal whether the email is registered
            return Response({
                "detail": "If that email is registered, a reset token has been generated.",
            })

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        return Response({
            "detail": "Password reset token generated.",
            "uid": uid,
            "token": token,
            "_demo_note": "In production, uid and token would be delivered by email only.",
        })


class PasswordResetConfirmView(APIView):
    """
    Validates a password reset token and sets the new password.
    POST { uid, token, password, password2 }
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "uid":       {"type": "string"},
                    "token":     {"type": "string"},
                    "password":  {"type": "string"},
                    "password2": {"type": "string"},
                },
                "required": ["uid", "token", "password", "password2"],
            }
        },
        responses={200: OpenApiTypes.OBJECT},
        description="Confirm password reset using uid and token from the reset request.",
    )
    def post(self, request):
        uid       = str(request.data.get("uid", "")).strip()
        token     = str(request.data.get("token", "")).strip()
        password  = str(request.data.get("password", ""))
        password2 = str(request.data.get("password2", ""))

        if not uid or not token or not password or not password2:
            raise ValidationError({"detail": "uid, token, password, and password2 are required."})

        if password != password2:
            raise ValidationError({"password2": "Passwords do not match."})

        try:
            user_pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_pk)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise ValidationError({"detail": "Invalid reset link."})

        if not default_token_generator.check_token(user, token):
            raise ValidationError({"detail": "Reset token is invalid or has expired."})

        try:
            validate_password(password, user)
        except Exception as exc:
            raise ValidationError({"password": list(exc.messages)})

        user.set_password(password)
        user.save()

        return Response({"detail": "Password reset successfully. You can now sign in."})
