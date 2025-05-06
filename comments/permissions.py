from rest_framework.permissions import BasePermission


class CommentOwner(BasePermission):
    """The owner has full access to their posts"""

    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user)
