from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile whenever a new User is created,
    so every account (including ones created via createsuperuser) has one.
    """
    if created:
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={'is_librarian': instance.is_superuser or instance.is_staff},
        )
    else:
        UserProfile.objects.get_or_create(user=instance)
