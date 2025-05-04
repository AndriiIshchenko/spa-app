from rest_framework import serializers

from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )

    class Meta:
        model = Comment
        fields = ("id", "user_profile", "content", "created_at")
