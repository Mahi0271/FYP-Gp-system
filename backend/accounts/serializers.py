from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from accounts.models import User


class PatientRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    # optional extras (keep if you want)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]

        # IMPORTANT: set role=PATIENT at creation time so your post_save signal runs
        user = User.objects.create_user(
            username=username,
            password=password,
            role=User.Role.PATIENT,
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

from .serializers import PatientRegisterSerializer


class PatientSignupView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=PatientRegisterSerializer,
        responses={201: OpenApiTypes.OBJECT},
        description="Patient signup (creates PATIENT user).",
    )
    def post(self, request):
        serializer = PatientRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # calls create()

        return Response(
            {
                "detail": "Signup successful.",
                "id": user.id,
                "username": user.username,
                "role": getattr(user, "role", None),
            },
            status=status.HTTP_201_CREATED,
        )
    
from rest_framework import serializers
from accounts.models import User, PatientProfile


class PatientContactUpdateSerializer(serializers.Serializer):
    # User fields (identity/contact)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    # PatientProfile contact fields
    phone = serializers.CharField(required=False, allow_blank=True)
    address_line1 = serializers.CharField(required=False, allow_blank=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    postcode = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def update(self, instance: User, validated_data):
        """
        instance is the PATIENT user.
        Updates User + PatientProfile fields.
        """
        # Update User fields
        for f in ["first_name", "last_name", "email"]:
            if f in validated_data:
                setattr(instance, f, validated_data[f])
        instance.save()

        # Update PatientProfile fields
        profile, _ = PatientProfile.objects.get_or_create(user=instance)

        for f in ["phone", "address_line1", "address_line2", "city", "postcode", "date_of_birth"]:
            if f in validated_data:
                setattr(profile, f, validated_data[f])
        profile.save()

        return instance