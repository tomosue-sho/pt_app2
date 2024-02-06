from django.db import models
from django.conf import settings

#試験年度用
class Exam(models.Model):
    year = models.IntegerField("年度", unique=True)

    def __str__(self):
        return f"{self.year}年度"
    
class QuizQuestion(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="年度")
    field = models.CharField("分野", max_length=100)
    sub_field = models.CharField("詳細分野", max_length=100, blank=True)
    point = models.IntegerField("配点", choices=((1, '1点'), (3, '3点')))
    question_number = models.IntegerField("問題番号")
    answer_time = models.IntegerField("回答時間（秒）")
    question_text = models.TextField("問題文")
    question_image = models.ImageField("問題画像", upload_to='quiz_questions/', blank=True, null=True)
    answer_text = models.TextField("解答分")
    answer_video_url = models.URLField("解答動画URL", blank=True, null=True)

    def __str__(self):
        return f"{self.year}年 {self.field} {self.question_number}問"
    
class QuestionUserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="ユーザー")
    exam_question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, verbose_name="問題")
    answer = models.TextField("ユーザーの回答")
    answered_at = models.DateTimeField("回答日時", auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.exam_question}"