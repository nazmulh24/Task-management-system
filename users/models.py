from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfiles(models.Model):
    user = models.OneToOneField(
        User, related_name="userprofile", on_delete=models.CASCADE, primary_key=True
    )
    profile_img = models.ImageField(upload_to="profile_images", blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} profile"
