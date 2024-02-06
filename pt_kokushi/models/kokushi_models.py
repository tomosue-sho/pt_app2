from django.db import models

#試験年度用
class Exam(models.Model):
    year = models.IntegerField(unique=True)