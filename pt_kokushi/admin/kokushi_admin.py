from django.contrib import admin
from pt_kokushi.models.kokushi_models import Exam,QuizQuestion,Bookmark
from pt_kokushi.models.kokushi_models import Choice,QuizUserAnswer,KokushiField

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('year',)
    
@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    def get_exam_year(self, obj):
        return obj.exam.year
    get_exam_year.short_description = '年度'
    get_exam_year.admin_order_field = 'exam__year'

    list_display = ('id','get_exam_year', 'field', 'point','time', 'question_number', 'answer_time', 'question_text', 'answer_video_url', 'question_image')
    search_fields = ('field', 'question_text')
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

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'created_at')
    search_fields = ('user__username', 'question__question_text')
    list_filter = ('user',)
    
class KokushiFieldAdmin(admin.ModelAdmin):
    list_display = ('name',)  # 管理サイトのリスト表示に名前を表示
    search_fields = ('name',)  # 名前で検索できるようにする
    
class QuizUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'display_selected_choices', 'start_time', 'end_time')
    list_filter = ('user', 'question')
    search_fields = ('user__username', 'question__question_text')

    def display_selected_choices(self, obj):
        """選択した選択肢のテキストを表示するためのメソッド"""
        return ", ".join([choice.choice_text for choice in obj.selected_choices.all()])
    display_selected_choices.short_description = "選択した選択肢"

admin.site.register(KokushiField, KokushiFieldAdmin)  
admin.site.register(QuizUserAnswer, QuizUserAnswerAdmin)
#admin.site.register(QuizQuestion, QuizQuestionAdmin)