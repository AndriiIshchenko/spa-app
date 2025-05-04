from django.urls import path, include
from rest_framework import routers

from comments.views import CommentViewSet


router = routers.DefaultRouter()

router.register("", CommentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "comments"
