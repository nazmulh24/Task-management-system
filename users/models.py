from django.db import models
from django.contrib.auth.models import AbstractUser


"""
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="userprofile",
    )
    profile_img = models.ImageField(upload_to="profile_images", blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} profile"
"""


class CustomUser(AbstractUser):
    profile_img = models.ImageField(upload_to="profile_images", blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username
