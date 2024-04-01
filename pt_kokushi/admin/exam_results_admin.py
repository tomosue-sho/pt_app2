from django.contrib import admin
from pt_kokushi.models.exam_results_models import ExamResult

@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ('exam_year', 'applicants_total', 'examinees_total', 'passers_total')
