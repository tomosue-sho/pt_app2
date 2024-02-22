from django import forms
from django.shortcuts import render, redirect
from pt_kokushi.models.studychart_models import StudyLog

class StudyLogForm(forms.ModelForm):
    class Meta:
        model = StudyLog
        fields = ['study_date', 'study_duration', 'study_content']
        widgets = {
            'study_date': forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
            'study_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'study_content': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'study_date': '学習日',
            'study_duration': '学習時間（分）',
            'study_content': '学習内容',
        }
