from django.db import models

class LearningMaterial(models.Model):
    field = models.CharField(max_length=100, verbose_name="分野")
    title = models.CharField(max_length=200, verbose_name="タイトル")
    file = models.FileField(upload_to='learning_materials/', verbose_name="ファイル")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "学習資料"
        verbose_name_plural = "学習資料"