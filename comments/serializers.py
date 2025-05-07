from typing import List
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from comments.models import Comment, UserProfile


class CommentSerializer(serializers.ModelSerializer):
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )

    class Meta:
        model = Comment
        fields = ("id", "user_profile", "content", "created_at")


class CommentListSerializer(serializers.ModelSerializer):
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )
    replies_count = serializers.SerializerMethodField()

    def get_replies_count(self, obj) -> int:
        return obj.replies.count()  # Count the number of replies

    class Meta:
        model = Comment
        fields = (
            "id",
            "parent_comment",
            "user_profile",
            "content",
            "created_at",
            "replies_count",
        )


class CommentDetailSerializer(serializers.ModelSerializer):
    user_profile = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="nickname"
    )
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "parent_comment", "user_profile", "content", "created_at", "replies")

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_replies(self, obj):
        # Get the request object
        request = self.context.get("request")

        # Paginate the replies queryset
        paginator = PageNumberPagination()  # LimitOffsetPagination()
        replies_queryset = obj.replies.all()  # Get all replies for the comment
        paginated_replies = paginator.paginate_queryset(replies_queryset, request)

        # Serialize the paginated replies
        serializer = CommentListSerializer(
            paginated_replies, many=True, context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data).data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "user", "nickname", "bio", "birth_date")
        read_only_fields = ("id", "user")


class UserProfileListSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ("id", "nickname", "user", "photo", "comments")

    def get_comments(self, obj) -> int:
        return obj.comments.count()


class UserProfileDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "nickname",
            "bio",
            "photo",
            "birth_date",
            "comments",
        ]

    def get_comments(self, obj) -> List[str]:

        comments = obj.comments.all()
        if not comments:
            return []
        all_comments = []
        for comment in comments:
            if comment.parent_comment:
                all_comments.append(
                    f"{comment.parent_comment.user_profile.nickname}"
                    f"posted: '{comment.parent_comment_content[0:30]}'."
                    f"Your comment: '{comment.content[:30]}'"
                )
            else:
                all_comments.append(
                    f"{comment.user_profile.nickname} posted: '{comment.content[:30]}'."
                )
        return all_comments


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "photo"]
