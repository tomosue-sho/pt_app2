from django.db import models
from django.conf import settings
from django.utils.timezone import now


#試験年度用
class Exam(models.Model):
    year = models.IntegerField("年度", unique=True)

    def __str__(self):
        return f"{self.year}回"
    
    class Meta:
        verbose_name = "国試「年度追加」" 
        verbose_name_plural = "国試「年度追加」" 

class KokushiField(models.Model):
    name = models.CharField("分野名", max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "国試「分野追加」"
        verbose_name_plural = "国試「分野追加」"
    
class QuizQuestion(models.Model):
    EXAM_TIME_CHOICES = (
        ('午前', '午前'),
        ('午後', '午後'),
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="年度")
    field = models.ForeignKey(KokushiField, on_delete=models.CASCADE, verbose_name="分野")
    point = models.IntegerField("配点", choices=((1, '1点'), (3, '3点')))
    time = models.CharField("午前・午後", max_length=2, choices=EXAM_TIME_CHOICES, default='午前')
    question_number = models.IntegerField("問題番号")
    answer_time = models.IntegerField("回答時間（秒）", blank=True, null=True)
    question_text = models.TextField("問題文")
    question_image = models.ImageField("問題画像", upload_to='quiz_questions/', blank=True, null=True)
    answer_text = models.TextField("解答分")
    answer_video_url = models.URLField("解答動画URL", blank=True, null=True)

    def __str__(self):
        return f"{self.exam.year}年 {self.time} {self.question_number}問" 
    
    def get_previous_question(self):
        """現在の問題の直前の問題を取得する"""
        previous_question = QuizQuestion.objects.filter(
            exam=self.exam,
            question_number__lt=self.question_number
        ).order_by('-question_number').first()
        return previous_question

    def has_previous(self):
        """直前の問題が存在するかどうかをチェックする"""
        return bool(self.get_previous_question())
    
    def correct_choices_count(self):
        return self.choices.filter(is_correct=True).count()
    
    class Meta:
        verbose_name = "国試「問題作成」"
        verbose_name_plural = "国試「問題作成」"

    
class Choice(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField("選択肢", max_length=255)
    is_correct = models.BooleanField("正解", default=False)
    
    class Meta:
        verbose_name = "国試「回答選択肢」" 
        verbose_name_plural = "国試「回答選択肢」"
    
class QuizUserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="ユーザー")
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, verbose_name="問題")
    selected_choices = models.ManyToManyField(Choice, verbose_name="選んだ選択肢")
    answered_at = models.DateTimeField("回答日時", auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    def is_correct(self):
        # すべての選択した選択肢が正解で、正解の選択肢をすべて選んでいるかをチェック
        correct_choices = self.question.choices.filter(is_correct=True)
        return set(self.selected_choices.all()) == set(correct_choices)
    
    def is_correct(self):
        correct_choices = self.question.choices.filter(is_correct=True)
        selected_correct_choices = self.selected_choices.filter(is_correct=True)
        # 選択された正解の選択肢が正しい選択肢すべてであり、かつ、選択された選択肢の数が正解の選択肢の数と一致するかチェック
        return set(selected_correct_choices) == set(correct_choices) and selected_correct_choices.count() == self.question.correct_choices_count()
    
class KokushiQuizSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="ユーザー")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="試験")
    start_time = models.DateTimeField("開始時刻", default=now)
    end_time = models.DateTimeField("終了時刻", null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.exam}"

    
class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="ユーザー")
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, verbose_name="ブックマークした問題")
    created_at = models.DateTimeField("ブックマーク日時", auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')  # ユーザーと問題の組み合わせはユニーク
        verbose_name = "国試「ブックマーク」" 
        verbose_name_plural = "国試「ブックマーク」" 

    def __str__(self):
        return f"{self.user} - {self.question}"