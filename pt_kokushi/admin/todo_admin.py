from django.contrib import admin
from pt_kokushi.models.todo_models import ToDoItem

class ToDoItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'purpose', 'priority', 'deadline', 'created_at', 'updated_at')
    list_filter = ('priority', 'deadline', 'created_at')
    search_fields = ('title', 'content')
    
admin.site.register(ToDoItem, ToDoItemAdmin)