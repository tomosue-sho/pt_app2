from django.db import models

#カレンダー機能用のmodels.py
class Event(models.Model):
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    user_email = models.EmailField()  # ユーザーのemailを直接保存

    def __str__(self):
        return self.title