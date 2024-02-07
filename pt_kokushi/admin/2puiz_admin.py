from django.contrib import admin
from pt_kokushi.models.question_models import Field, Subfield, Sub2field
from pt_kokushi.models.question_models import Question, UserAnswer, UserScore
from django.utils.html import format_html

class FieldAdmin(admin.ModelAdmin):
    list_display = ('custom_name', 'custom_description', 'custom_icon') 

    def custom_name(self, obj):
        return obj.name
    custom_name.short_description = "分野名"

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = "説明"

    def custom_icon(self, obj): 
        
        if obj.icon:
            return format_html('<img src="{}" width="50" height="50" />', obj.icon.url)
        else:
            return "No Icon"  # アイコンが設定されていない場合のテキスト

    custom_icon.short_description = "アイコン"
    
    
class SubfieldAdmin(admin.ModelAdmin):
    list_display = ('custom_name', 'custom_description', 'custom_icon', 'field', 'has_detailed_selection')
    list_filter = ('name', 'field')

    def custom_name(self, obj):
        return obj.name
    custom_name.short_description = "分野名"

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = "説明"

    def custom_icon(self, obj):
        return obj.icon 
    custom_icon.short_description = "アイコン"

class Sub2fieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_icon', 'subfield')
    list_filter = ['subfield',]

    def display_icon(self, obj):
        return obj.icon.url if obj.icon else 'No Icon'
    display_icon.short_description = "アイコン"
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text',  'field' ,'subfield', 'sub2field', 'correct_answer')
    list_filter = ('field','subfield', 'sub2field')
    search_fields = ('question_text',)
    
admin.site.register(Field, FieldAdmin)
admin.site.register(Subfield, SubfieldAdmin)
admin.site.register(Sub2field, Sub2fieldAdmin)
admin.site.register(Question, QuestionAdmin)