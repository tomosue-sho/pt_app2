from django.db import models

#掲示板機能用のmodels.py    
class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="投稿日時")
    nickname = models.CharField(max_length=20, verbose_name="ニックネーム",blank=True)
    last_commented_at = models.DateTimeField(auto_now=True, verbose_name="最終コメント日時")
    ordering = ['-last_commented_at']
    view_count = models.PositiveIntegerField(default=0, verbose_name="ビュー数")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-last_commented_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="対応する投稿")
    content = models.TextField(verbose_name="コメント内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="コメント日時")
    nickname = models.CharField(max_length=20, verbose_name="ニックネーム",blank=True) 

    def __str__(self):
      return f"{self.nickname} - {self.post.title}"
