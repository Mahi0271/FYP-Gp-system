from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate

import pyotp
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from .models import User
from .serializers import PatientContactUpdateSerializer

from audits.utils import log_event


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            "id": u.id,
            "username": u.username,
            "role": getattr(u, "role", None),
            "mfa_enabled": bool(getattr(u, "mfa_enabled", False)),
        })


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

        # Receptionist-only (superuser allowed)
        if not (u.is_superuser or u.role == User.Role.RECEPTIONIST):
            raise PermissionDenied("Only receptionists can update patient contact details.")

        try:
            patient = User.objects.get(id=patient_id, role=User.Role.PATIENT)
        except User.DoesNotExist:
            raise NotFound("Patient not found.")

        serializer = PatientContactUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(patient, serializer.validated_data)

        # Audit log (recommended for FR14 accountability)
        log_event(
            request,
            action="PATIENT_CONTACT_UPDATE",
            obj=patient,
            object_type="user",
            metadata={"patient_id": patient.id},
        )

        # Return updated data (clean response)
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
    You can paste the otpauth URL into a QR generator or directly into an authenticator app.
    """
    permission_classes = [IsAuthenticated]

    

    def post(self, request):
        u: User = request.user

        # Generate a new secret (base32)
        secret = pyotp.random_base32()
        u.mfa_secret = secret
        u.mfa_enabled = False  # will be enabled only after verify
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
            "properties": {
                "code": {"type": "string", "example": "123456"},
            },
            "required": ["code"],
        }
    },
    responses={200: OpenApiTypes.OBJECT},
    description="Disable MFA for the authenticated user. Requires a valid 6-digit TOTP code.",
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
            "properties": {
                "code": {"type": "string", "example": "123456"},
            },
            "required": ["code"],
        }
    },
    responses={200: OpenApiTypes.OBJECT},
    description="Enable MFA for the authenticated user. Requires a valid 6-digit TOTP code.",
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

        # Disable MFA (keep secret so you can re-enable without re-setup; or clear it if you prefer)
        u.mfa_enabled = False
        u.save(update_fields=["mfa_enabled"])

        return Response({"mfa_enabled": False, "detail": "MFA disabled."})


class MFAVerifyLoginView(APIView):
    """
    Login endpoint for MFA-enabled users.
    POST { username, password, code } -> returns JWT pair if correct.
    For non-MFA users, you can still use /api/token/ as normal.
    """
    authentication_classes = []  # allow anonymous
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

        # If user doesn't have MFA enabled, we still allow this endpoint (optional)
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
    


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from .serializers import PatientRegisterSerializer


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