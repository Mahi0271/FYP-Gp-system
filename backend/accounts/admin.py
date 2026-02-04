from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, GPProfile, PatientProfile


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    # Show role in list view
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")

    # Add role to the edit page
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

    # Add role to the "Add user" page (the one you're on now)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


admin.site.register(GPProfile)
admin.site.register(PatientProfile)
