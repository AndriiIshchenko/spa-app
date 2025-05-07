import os
import tempfile
from PIL import Image

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from comments.models import Comment, UserProfile
from comments.serializers import (
    CommentSerializer,
    CommentDetailSerializer,
    UserProfileSerializer,
    UserProfileDetailSerializer,
)

COMMENT_URL = reverse("comments:comment-list")
USER_PROFILE_URL = reverse("comments:userprofile-list")


def comment_detail_url(comment_id) -> str:
    return reverse("comments:comment-detail", args=[comment_id])


def user_profile_detail_url(profile_id) -> str:
    return reverse("comments:userprofile-detail", args=[profile_id])


def upload_image_url(profile_id) -> str:
    return reverse("comments:userprofile-upload-image", args=[profile_id])


class TestCommentViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@myproject.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)
        self.profile = UserProfile.objects.create(user=self.user, nickname="testnick")
        self.comment = Comment.objects.create(
            user_profile=self.profile,
            content="Test Comment",
        )

    def test_create_comment(self):
        data = {
            "content": "New Comment",
            "user_profile": self.profile.id,
        }
        response = self.client.post(COMMENT_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_data = CommentSerializer(
            Comment.objects.get(id=response.data["id"])
        ).data
        self.assertEqual(response.data, expected_data)

#     def test_retrieve_comment(self):
#         url = comment_detail_url(self.comment.pk)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         expected_data = CommentDetailSerializer(self.comment).data
#         self.assertEqual(response.data, expected_data)

#     def test_update_comment(self):
#         url = comment_detail_url(self.comment.pk)
#         data = {"content": "Updated Comment"}
#         response = self.client.put(url, data=data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.comment.refresh_from_db()
#         expected_data = CommentDetailSerializer(self.comment).data
#         self.assertEqual(response.data, expected_data)

#     def test_delete_comment(self):
#         url = comment_detail_url(self.comment.pk)
#         response = self.client.delete(url)
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Comment.objects.filter(id=self.comment.pk).exists())


# class TestUserProfileViewSet(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             email="test@myproject.com", password="testpass123"
#         )
#         self.client.force_authenticate(user=self.user)
#         self.profile = UserProfile.objects.create(user=self.user, nickname="testnick")

#     def test_retrieve_user_profile(self):
#         url = user_profile_detail_url(self.profile.pk)
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         expected_data = UserProfileDetailSerializer(self.profile).data
#         self.assertEqual(response.data, expected_data)

#     def test_update_user_profile(self):
#         url = user_profile_detail_url(self.profile.pk)
#         data = {"nickname": "UpdatedNick"}
#         response = self.client.patch(url, data=data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.profile.refresh_from_db()
#         self.assertEqual(self.profile.nickname, "UpdatedNick")

#     def test_upload_image_to_user_profile(self):
#         """Test uploading an image to user profile"""
#         url = upload_image_url(self.profile.id)
#         with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
#             img = Image.new("RGB", (10, 10))
#             img.save(ntf, format="JPEG")
#             ntf.seek(0)
#             res = self.client.post(url, {"photo": ntf}, format="multipart")
#         self.profile.refresh_from_db()

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn("photo", res.data)
#         self.assertTrue(os.path.exists(self.profile.photo.path))

#     def test_upload_image_bad_request(self):
#         """Test uploading an invalid image"""
#         url = upload_image_url(self.profile.id)
#         res = self.client.post(url, {"photo": "not an image"}, format="multipart")

#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_list_user_profiles(self):
#         response = self.client.get(USER_PROFILE_URL)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         expected_data = UserProfileSerializer(UserProfile.objects.all(), many=True).data
#         self.assertEqual(response.data, expected_data)
