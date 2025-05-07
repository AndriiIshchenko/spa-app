from django.contrib import admin

from comments.models import Comment, UserProfile


admin.site.register(UserProfile)
admin.site.register(Comment)
