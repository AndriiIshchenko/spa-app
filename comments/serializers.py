from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

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
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "parent_comment", "user", "content", "created_at", "replies")

    def get_replies(self, obj):
        # Get the request object
        request = self.context.get("request")

        # Paginate the replies queryset
        paginator = PageNumberPagination() #LimitOffsetPagination()
        replies_queryset = obj.replies.all()  # Get all replies for the comment
        paginated_replies = paginator.paginate_queryset(replies_queryset, request)

        # Serialize the paginated replies
        serializer = CommentListSerializer(
            paginated_replies, many=True, context={"request": request}
        )
        
        return paginator.get_paginated_response(serializer.data).data
       
        # return {
        #     "count": paginator.count,
        #     "next": paginator.get_next_link(),
        #     "previous": paginator.get_previous_link(),
        #     "results": serializer.data,
        # }
