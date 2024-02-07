from django.contrib import admin
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion,QuestionUserAnswer,Bookmark,Choice,QuizUserAnswer

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('year',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    def get_exam_year(self, obj):
        return obj.exam.year
    get_exam_year.short_description = '年度'
    get_exam_year.admin_order_field = 'exam__year'

    list_display = ('get_exam_year', 'field', 'sub_field', 'point', 'question_number', 'answer_time', 'question_text', 'answer_video_url', 'question_image')
    search_fields = ('field', 'sub_field', 'question_text')
    list_filter = ('exam__year', 'field', 'point')

    # 選択肢をインラインで表示するための設定
    class ChoiceInline(admin.TabularInline):
        model = Choice
        extra = 3  # デフォルトで3つの選択肢フィールドを表示

    inlines = [ChoiceInline]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_text', 'is_correct')
    list_filter = ('question', 'is_correct')
    search_fields = ('choice_text',)

@admin.register(QuestionUserAnswer)  # ここを正しいモデル名に修正
class QuestionUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'exam_question', 'answer', 'answered_at')  # 'question' を 'exam_question' に修正
    search_fields = ('user__username', 'exam_question__question_text', 'answer')  # 修正箇所を確認
    list_filter = ('user', 'exam_question')  # 'exam_question' を正しく指定

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    search_fields = ('user__username', 'question__question_text')
    list_filter = ('user',)
    
#admin.site.register(QuizQuestion, QuizQuestionAdmin)
#admin.site.register(QuizUserAnswer, QuizUserAnswerAdmin)