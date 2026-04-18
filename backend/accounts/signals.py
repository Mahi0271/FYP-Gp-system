"""
Django signals for the accounts app.

Signals are Django's way of running code automatically in response to
database events without the caller needing to know about it.

This file wires up one signal:
  post_save on User → create_profile
    - When a new GP account is created, automatically create a GPProfile for them.
    - When a new PATIENT account is created, automatically create a PatientProfile
      and assign them to whichever GP currently has the fewest patients
      (simple load-balancing so no single GP gets overwhelmed).
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count

from .models import User, GPProfile, PatientProfile


def pick_gp_for_new_patient() -> GPProfile | None:
    """
    Find the GP with the smallest current patient list.

    Annotates every GPProfile with a patient count (using the 'patients'
    reverse relation defined on PatientProfile.assigned_gp), then sorts
    ascending so the least-busy GP comes first.  Returns None if there are
    no GPs in the system yet.
    """
    return (
        GPProfile.objects
        .annotate(num_patients=Count("patients"))  # 'patients' is the related_name on PatientProfile.assigned_gp
        .order_by("num_patients", "id")            # tie-break by id so the result is deterministic
        .first()
    )


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created: bool, **kwargs):
    """
    Automatically create the correct profile record whenever a new User is saved.

    'created' is True only on INSERT (not on UPDATE), so this code runs once
    per user and never accidentally recreates profiles on every .save() call.
    """
    if not created:
        return  # nothing to do for updates — only act on brand-new users

    if instance.role == User.Role.GP:
        # Every GP needs a GPProfile so patients can be linked to them
        GPProfile.objects.create(user=instance)

    elif instance.role == User.Role.PATIENT:
        # Assign the new patient to the least-loaded GP automatically
        gp_profile = pick_gp_for_new_patient()
        PatientProfile.objects.create(user=instance, assigned_gp=gp_profile)