"""
Serializers for the accounts app — handles input validation and data shaping
for patient registration and patient contact detail updates.

PatientRegisterSerializer  → validates a new patient sign-up form
PatientContactUpdateSerializer → validates a receptionist's PATCH request
                                  to update a patient's personal details
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import User, PatientProfile


class PatientRegisterSerializer(serializers.Serializer):
    """
    Validates and creates a new PATIENT user account.

    Enforces:
      - Username uniqueness
      - Password confirmation (password == password2)
      - Django's built-in password strength rules (length, common passwords, etc.)

    The role is always forced to PATIENT here — only admins can create
    GP, Receptionist, or Manager accounts via the Django admin panel.
    """
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)   # write_only → never returned in responses
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        """Reject the request early if the username is already taken."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate(self, attrs):
        """Check passwords match, then run Django's password strength validators."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        """Create the user. Django's create_user hashes the password before saving."""
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            role=User.Role.PATIENT,
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )


class PatientContactUpdateSerializer(serializers.Serializer):
    """
    Validates a partial update to a patient's contact information.

    All fields are optional (supports PATCH semantics) — only the fields
    sent in the request are updated. Fields on the User model (name, email)
    are saved separately from fields on the PatientProfile model (phone, address).
    """
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    address_line1 = serializers.CharField(required=False, allow_blank=True)
    address_line2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    postcode = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def update(self, instance: User, validated_data):
        """
        Apply changes to both the User row and the linked PatientProfile row.

        get_or_create ensures a PatientProfile exists even if it was somehow
        never created by the signal (defensive coding).
        """
        # Update name/email fields that live directly on the User model
        for f in ["first_name", "last_name", "email"]:
            if f in validated_data:
                setattr(instance, f, validated_data[f])
        instance.save()

        # Update contact fields that live on the separate PatientProfile model
        profile, _ = PatientProfile.objects.get_or_create(user=instance)

        for f in ["phone", "address_line1", "address_line2", "city", "postcode", "date_of_birth"]:
            if f in validated_data:
                setattr(profile, f, validated_data[f])
        profile.save()

        return instance
