import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.conf import settings


def profile_image_path(instance, filename) -> str:
    _, extention = os.path.splitext(filename)
    filename = f"{slugify(instance.nickname)}-{uuid.uuid4()}{extention}"
    return os.path.join("uploads/profile/", filename)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    nickname = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True, null=True)
    birth_date = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(blank=True, null=True, upload_to=profile_image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nickname


def comment_image_path(instance, filename) -> str:
    _, extention = os.path.splitext(filename)
    filename = f"{slugify(instance.user)}-{uuid.uuid4()}{extention}"
    return os.path.join("uploads/post/", filename)


class Comment(models.Model):
    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="comments"
    )
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies"
    )
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=True, null=True, upload_to=comment_image_path)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment to {self.parent_comment} by {self.user}"
