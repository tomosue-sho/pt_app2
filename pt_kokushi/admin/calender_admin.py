from django.contrib import admin
from pt_kokushi.models.calender_models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'user_email')