from django.db import models

#ToDoリストのmodels.py
class ToDoItem(models.Model):
    # 優先度を表す選択肢
    PRIORITY_CHOICES = [
        (1, '低'),
        (2, '中'),
        (3, '高'),
    ]

    title = models.CharField(max_length=100, verbose_name="タイトル")
    content = models.TextField(verbose_name="内容")
    purpose = models.TextField(verbose_name="目的", blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name="優先度")
    deadline = models.DateField(verbose_name="期限", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-priority', '-created_at']  # 優先度が高く、作成日が新しい順に並べる