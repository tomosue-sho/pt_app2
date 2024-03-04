from django.contrib import admin
from pt_kokushi.models.relax_models import Column

class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date') # 管理リストに表示するフィールド
    list_filter = ('published_date',) # リストページでフィルタリングできるフィールド
    search_fields = ('title', 'content') # 検索可能なフィールド
    date_hierarchy = 'published_date' # 日付で階層的に探索できるようにする
    ordering = ('-published_date',) # デフォルトの並び順
    fields = ('title', 'content', 'published_date') # 編集フォームに表示するフィールド
    readonly_fields = ('published_date',) # 編集不可にするフィールド

admin.site.register(Column, ColumnAdmin)
