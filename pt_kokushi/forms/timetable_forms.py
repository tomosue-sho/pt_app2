from django import forms
from pt_kokushi.models.timetable_models import TimeTable

#時間割用forms.py
class TimeTableForm(forms.ModelForm):
    class Meta:
        model = TimeTable
        fields = ['day', 'period', 'subject']
        labels = {
            'day': '曜日',
            'time_slot': '時間帯',
            'subject': '科目名',
            'period':'時限'
        }