from rest_framework import serializers

from comments.models import Comment


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")

    class Meta:
        model = Comment
        fields = ("id", "user", "content", "created_at")


class CommentListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    replies_count = serializers.SerializerMethodField()

    def get_replies_count(self, obj):
        return obj.replies.count()  # Count the number of replies

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent_comment",
            "user",
            "content",
            "created_at",
            "replies_count",
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(many=False, read_only=True, slug_field="email")
    replies = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "parent_comment", "user", "content", "created_at", "replies")
