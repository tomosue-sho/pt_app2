from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser
from .models import ToDoItem
from .models import Post, Comment
from .models import Event
from .models import TimeTable
from .models import Field, Subfield, Sub2field
from .models import Question, UserAnswer, UserScore


CustomUser = get_user_model()

#第２引数にModelAdminを継承することでクラスをカスタマイズできる
class CustomUserAdmin(admin.ModelAdmin):
    #管理画面に表示したい項目
    list_display = (
        'nickname',
        'email',
        'birth_of_date',
        'get_age',
        'school_year',
        'prefecture',
        'gender',
        'is_active',
        'date_joined',
        "is_staff",
        'test_year'
    )
    
    # 一覧画面: サイドバーフィルター
    list_filter = (
        "email",
        "is_staff",
    )

    # 一覧画面: 検索ボックス
    search_fields = ("email","nickname")

    # 一覧画面: ソート（降順ならフィールド名の先頭に-）
    ordering = ("email",)

    auth = ("is_staff", "is_active")
    
    #「[('好きな名前', {'fields': ('フィールド名',)})]」でフィールドのレイアウトを変更する
    fieldsets = (
        ("重要項目", {"fields": ( "email", "password")}),
        ("Personal", {"fields": ( "nickname","birth_of_date","school_year","prefecture","gender","test_year")}),
        ("Auth", {"fields": ("is_staff", "is_active","date_joined"),}),
    )
    
class ToDoItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'purpose', 'priority', 'deadline', 'created_at', 'updated_at')
    list_filter = ('priority', 'deadline', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'created_at', 'nickname')
    
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'user_email')
    
@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('day', 'get_period_display', 'subject')
    
class FieldAdmin(admin.ModelAdmin):
    list_display = ('custom_name', 'custom_description', 'custom_icon') 

    def custom_name(self, obj):
        return obj.name
    custom_name.short_description = "分野名"

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = "説明"

    def custom_icon(self, obj):
        # 画像のフルパスを文字列として返す
        if obj.icon:
            return format_html('<img src="{}" width="50" height="50" />', obj.icon.url)
        else:
            return "No Icon"  # アイコンが設定されていない場合のテキスト

    custom_icon.short_description = "アイコン"
    
    
class SubfieldAdmin(admin.ModelAdmin):
    list_display = ('custom_name', 'custom_description', 'custom_icon', 'field', 'has_detailed_selection')

    def custom_name(self, obj):
        return obj.name
    custom_name.short_description = "分野名"

    def custom_description(self, obj):
        return obj.description
    custom_description.short_description = "説明"

    def custom_icon(self, obj):
        return obj.icon  # ここでは画像の表示方法を指定する必要があります
    custom_icon.short_description = "アイコン"

class Sub2fieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'display_icon', 'subfield')

    def display_icon(self, obj):
        return obj.icon.url if obj.icon else 'No Icon'
    display_icon.short_description = "アイコン"
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'field', 'subfield', 'sub2field', 'correct_answer')
    list_filter = ('field', 'subfield', 'sub2field')
    search_fields = ('question_text',)


#モデルをAdminページで見えるようにするためにはadmin.site.registerで登録する必要がある
#registerの第２引数にクラス名を指定する必要がある
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(ToDoItem, ToDoItemAdmin)
admin.site.register(Field, FieldAdmin)
admin.site.register(Subfield, SubfieldAdmin)
admin.site.register(Sub2field, Sub2fieldAdmin)
admin.site.register(Question, QuestionAdmin)
