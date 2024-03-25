from django import forms
from pt_kokushi.models.inquiry_models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('name', 'email', 'message',)
