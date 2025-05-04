import os
import uuid

from django.db import models
from django.utils.text import slugify


def comment_image_path(instance, filename) -> str:
    _, extention = os.path.splitext(filename)
    filename = f"{slugify(instance.user_profile.nickname)}-{uuid.uuid4()}{extention}"
    return os.path.join("uploads/post/", filename)


class Comment(models.Model):
    # user_profile = models.ForeignKey(
    #     UserProfile, on_delete=models.CASCADE, related_name="posts"
    # )
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="replies"
    )
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(blank=True, null=True, upload_to=comment_image_path)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment to {self.parent_comment} by {self.user_profile}"
