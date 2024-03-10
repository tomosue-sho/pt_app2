from django.contrib import admin
from django.utils.html import format_html
from pt_kokushi.models.relax_models import Column,AozoraBook

class ColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date') # 管理リストに表示するフィールド
    list_filter = ('published_date',) # リストページでフィルタリングできるフィールド
    search_fields = ('title', 'content') # 検索可能なフィールド
    date_hierarchy = 'published_date' # 日付で階層的に探索できるようにする
    ordering = ('-published_date',) # デフォルトの並び順
    fields = ('title', 'content', 'published_date') # 編集フォームに表示するフィールド
    readonly_fields = ('published_date',) # 編集不可にするフィールド
    
class AozoraBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_content')  # 一覧表示に表示するフィールド
    search_fields = ('title', 'content')  # 検索フィールド
    
    def short_content(self, obj):
       
        return format_html("<span title='{}'>{}</span>", obj.content, obj.content[:10] + '...' if len(obj.content) > 10 else obj.content)
    
    short_content.short_description = '内容（抜粋）'  # カラムヘッダのタイトル

admin.site.register(Column, ColumnAdmin)
admin.site.register(AozoraBook, AozoraBookAdmin)
