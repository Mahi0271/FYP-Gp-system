"""
Django admin configuration for the accounts app.

Registers the User, GPProfile, and PatientProfile models so they're
manageable through the /admin/ panel.

The custom UserAdmin extends Django's built-in UserAdmin so we keep
all the standard fields (password hashing, permissions, etc.) while
also exposing the 'role' field that controls what each user can do.

Admins use this panel to:
  - Create GP, Receptionist, and Practice Manager accounts
    (patients self-register via the public sign-up page)
  - Activate / deactivate users
  - View and update user roles
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, GPProfile, PatientProfile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Columns shown in the user list page
    list_display = ("username", "email", "role", "is_staff", "is_active")
    # Sidebar filters on the list page
    list_filter = ("role", "is_staff", "is_active")

    # Append a "Role" section below the standard fieldsets on the edit page
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

    # Also show the role field when creating a brand-new user via the admin
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


# Register the profile models with default admin views so they're visible
admin.site.register(GPProfile)
admin.site.register(PatientProfile)
