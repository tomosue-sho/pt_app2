from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

CustomUser = get_user_model()

class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
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

    # 詳細画面: 表示項目
    basic = ("username", "email", "password")
    personal = ("last_name", "first_name", "date_joined")
    auth = ("is_staff", "is_active")

    fieldsets = (
        ("BasicInfo", {"fields": basic}),
        ("Personal", {"fields": personal}),
        ("Auth", {"fields": auth}),
    )
admin.site.register(CustomUser, CustomUserAdmin)

