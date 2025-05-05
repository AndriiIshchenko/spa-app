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
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        return CommentSerializer

    @action(
        detail=True,
        methods=["post"],
        url_path="replie",
        permission_classes=(IsAuthenticated,),
    )
    def replie(self, request, pk=None):
        parent_comment = self.get_object()
        user = request.user
        replie = Comment.objects.create(
            user=user,
            parent_comment=parent_comment,
            content=request.data.get("content"),
        )
        serializer = self.get_serializer(replie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
