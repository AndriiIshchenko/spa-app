from django.urls import path, include
from rest_framework import routers

from comments.views import CommentViewSet, CreateProfile, UserProfileViewSet


router = routers.DefaultRouter()

router.register("comments", CommentViewSet)
router.register("profiles", UserProfileViewSet)
router.register("create-profile", CreateProfile, basename="create-profile")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "comments"
