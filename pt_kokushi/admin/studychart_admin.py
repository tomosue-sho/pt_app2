from django.contrib import admin
from pt_kokushi.models.studychart_models import StudyLog

class StudyLogAdmin(admin.ModelAdmin):
    list_display = ( 'study_date', 'study_duration',) 
    list_filter = ('study_date', 'user',)  

admin.site.register(StudyLog, StudyLogAdmin)
