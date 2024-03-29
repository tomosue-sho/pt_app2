from django.conf import settings
from django.db import models

class StudyLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="ユーザー"
    )
    study_date = models.DateField(verbose_name="学習日")
    study_duration = models.IntegerField(verbose_name="学習時間（分）")
    study_content = models.TextField(verbose_name="学習内容", default='') 

    def __str__(self):
        return f"{self.user.email} - {self.study_date} - {self.study_duration}分"