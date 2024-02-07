from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

#4択問題用のmodels.py
#基礎学習分野選択ページ
class Field(models.Model):
    name = models.CharField(max_length=100, verbose_name="分野名")
    description = models.TextField(verbose_name="説明")
    icon = models.ImageField(upload_to='field_icons/', blank=True, null=True, verbose_name="アイコン")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "基礎学習「分野追加」" 
        verbose_name_plural = "基礎学習「分野追加」" 

class Subfield(models.Model):
    has_detailed_selection = models.BooleanField(default=False, verbose_name='さらに詳細な分野選択を可能にする')
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="分野名")
    description = models.TextField(verbose_name="説明")
    icon = models.ImageField(upload_to='subfield_icons/', blank=True, null=True, verbose_name="アイコン")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "基礎学習「詳細分野追加」" 
        verbose_name_plural = "基礎学習「詳細分野追加」"
    
class Sub2field(models.Model):
    subfield = models.ForeignKey(Subfield, on_delete=models.CASCADE, related_name='sub2fields')
    has_detailed_selection = models.BooleanField(default=False, verbose_name='さらに詳細な分野選択')
    name = models.CharField(max_length=100, verbose_name="分野名")
    description = models.TextField(verbose_name="説明")
    icon = models.ImageField(upload_to='subfield_icons/', blank=True, null=True, verbose_name="アイコン")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "基礎学習「補足詳細分野追加」" 
        verbose_name_plural = "基礎学習「補足詳細分野追加」"
    
class Question(models.Model):
    
    question_text = models.TextField()
    field = models.ForeignKey(Field, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    subfield = models.ForeignKey(Subfield, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    sub2field = models.ForeignKey(Sub2field, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    score = models.IntegerField(default=1) 
    choice1 = models.CharField(max_length=200)  # 選択肢1
    choice2 = models.CharField(max_length=200)  # 選択肢2
    choice3 = models.CharField(max_length=200)  # 選択肢3
    choice4 = models.CharField(max_length=200)  # 選択肢4
    
    correct_answer = models.CharField(max_length=1, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])
    
    def __str__(self):
        return self.question_text
    
    def save(self, *args, **kwargs):
        # subfield と sub2field の整合性をチェック
        if self.sub2field and self.subfield != self.sub2field.subfield:
            raise ValidationError("選択した sub2field は選択した subfield に属していません。")

        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "基礎学習「問題作成」" 
        verbose_name_plural = "基礎学習「問題作成」"
    
# ユーザーの回答を記録するモデル
class UserAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')])
    timestamp = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Answer: {self.question.question_text}"


# ユーザーのスコアを記録するモデル
class UserScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.IntegerField(default=0)
    total_questions_attempted = models.IntegerField(default=0)
    total_correct_answers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Score: {self.total_score}"

    def update_score(self, question, selected_answer):
        # ユーザーの回答と正解を比較してスコアを更新するメソッドを追加できます
        if selected_answer == question.correct_answer:
            self.total_correct_answers += 1
            self.total_score += 1
        self.total_questions_attempted += 1
        self.save()
        
class QuizSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    correct_answers = models.IntegerField(default=0)  # 正解数
    total_questions = models.IntegerField(default=5)  # クイズの問題数、ここでは5と仮定

    def __str__(self):
        return f"{self.user.username} - Session {self.id}"