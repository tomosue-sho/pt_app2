from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

CustomUser = get_user_model()

#第２引数にModelAdminを継承することでクラスをカスタマイズできる
class CustomUserAdmin(admin.ModelAdmin):
    #管理画面に表示したい項目
    list_display = (
        'email',
        'date_of_birth',
        'get_age',
        'school_year',
        'prefecture',
        'is_active',
        'date_joined',
        "is_staff",
    )
    
    # 一覧画面: サイドバーフィルター
    list_filter = (
        "email",
        "is_staff",
    )

    # 一覧画面: 検索ボックス
    search_fields = ("email",)

    # 一覧画面: ソート（降順ならフィールド名の先頭に-）
    ordering = ("email",)

    auth = ("is_staff", "is_active")
    
    #「[('好きな名前', {'fields': ('フィールド名',)})]」でフィールドのレイアウトを変更する
    fieldsets = (
        ("重要項目", {"fields": ('username', "email", "password")}),
        ("Personal", {"fields": ( "date_joined",)}),
        ("Auth", {"fields": ("is_staff", "is_active"),}),
    )
    
#モデルをAdminページで見えるようにするためにはadmin.site.registerで登録する必要がある
#registerの第２引数にクラス名を指定する必要がある
admin.site.register(CustomUser, CustomUserAdmin)

