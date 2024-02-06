from django import forms
from django.utils import timezone
from django.forms import ModelForm
from pt_kokushi.models.calender_models import Event

#カレンダーイベント追記用
class EventForm(ModelForm):
    start_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        initial=timezone.now().date(),
        widget=forms.SelectDateWidget(
            years=range(timezone.now().year, timezone.now().year - 10, -1),
            empty_label=("Year", "Month", "Day"),
        )
    )
    end_date = forms.DateField(
        input_formats=['%Y-%m-%d'],
        initial=timezone.now().date(),
        widget=forms.SelectDateWidget(
            years=range(timezone.now().year, timezone.now().year - 10, -1),
            empty_label=("Year", "Month", "Day"),
        )
    )

    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date']
        