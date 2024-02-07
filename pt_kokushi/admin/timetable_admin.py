from django.contrib import admin
from pt_kokushi.models.timetable_models import TimeTable

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('day', 'get_period_display', 'subject')