from django.contrib import admin
from pt_kokushi.models.post_models import Post, Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'created_at', 'nickname')