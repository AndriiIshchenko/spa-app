from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


from comments.permissions import CommentOwner
from comments.models import Comment, UserProfile
from comments.serializers import (
    CommentDetailSerializer,
    CommentSerializer,
    CommentListSerializer,
    UserProfileDetailSerializer,
    UserProfileImageSerializer,
    UserProfileListSerializer,
    UserProfileSerializer,
)


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

    def get_permissions(self):
        if self.action in ["create", "replie"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), CommentOwner()]
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return super().get_permissions()

    def get_queryset(self):

        queryset = self.queryset.filter(parent_comment__isnull=True)

        nickname = self.request.query_params.get("nickname")
        email = self.request.query_params.get("email")
        if nickname:
            queryset = queryset.filter(user_profile__nickname__icontains=nickname)
        if email:
            queryset = queryset.filter(user_profile__user__icontains=email)

        ordering = self.request.query_params.get("ordering")
        ordering_types = {"date": "created_at", 
                          "nickname": "user_profile__nickname", 
                          "email": "user_profile__user"}
        if ordering and ordering.lstrip("-") in ordering_types:
            if ordering.startswith("-"):
                ordering = "-" + ordering_types[ordering.lstrip("-")]
            else:
                ordering = ordering_types[ordering]
            queryset = queryset.order_by(ordering)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        return CommentSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number for pagination",
            ),
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nickname",
                description="Filter comments by user profile nickname (e.g., ?nickname=alice)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="email",
                description="Filter comments by user email (e.g., ?email=user@example.com)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="ordering",
                description=(
                    "Order comments by a specific field. "
                    "Available options: `date` (created_at), `nickname` (user_profile__nickname), "
                    "`email` (user_profile__user). Prefix with `-` for descending order "
                    "(e.g., ?ordering=-date)."
                ),
                required=False,
                type=OpenApiTypes.STR,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class CreateProfile(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        if UserProfile.objects.filter(user=self.request.user).exists():
            raise ValidationError("User already has profile")
        serializer.save(user=self.request.user)


class UserProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = (
        UserProfile.objects.all()
        .select_related(
            "user",
        )
        .prefetch_related(
            "posts__comments",
            "user__likes__post",
            "following",
            "followers",
        )
    )
    serializer_class = UserProfileSerializer

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), CommentOwner()]
        return super().get_permissions()

    def get_queryset(self):
        """Retrieve the user's profiles with filter"""
        queryset = self.queryset

        nickname = self.request.query_params.get("nickname")
        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserProfileListSerializer
        if self.action == "retrieve":
            return UserProfileDetailSerializer
        if self.action == "upload_image":
            return UserProfileImageSerializer
        return UserProfileSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nickname",
                description="Filter by nickname (ex. ?nickname=alice)",
                required=False,
                type=OpenApiTypes.STR,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
