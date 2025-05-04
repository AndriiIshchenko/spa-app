from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from comments.models import Comment
from comments.serializers import CommentSerializer

class CommentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
