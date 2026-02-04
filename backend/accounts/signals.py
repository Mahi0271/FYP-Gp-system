from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count

from .models import User, GPProfile, PatientProfile


def pick_gp_for_new_patient() -> GPProfile | None:
    # Choose the GP with the fewest assigned patients
    return (
        GPProfile.objects
        .annotate(num_patients=Count("patients"))  # because related_name="patients" on assigned_gp
        .order_by("num_patients", "id")
        .first()
    )


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return

    if instance.role == User.Role.GP:
        GPProfile.objects.create(user=instance)

    elif instance.role == User.Role.PATIENT:
        gp_profile = pick_gp_for_new_patient()
        PatientProfile.objects.create(user=instance, assigned_gp=gp_profile)
