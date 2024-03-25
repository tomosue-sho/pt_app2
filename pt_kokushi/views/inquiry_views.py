from django.shortcuts import render, redirect
from pt_kokushi.forms.inquiry_forms import InquiryForm

def inquiry_view(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pt_kokushi:thank_you')
    else:
        form = InquiryForm()
    return render(request, 'inquiry/inquiry_form.html', {'form': form})

def thank_you_view(request):
    return render(request, 'inquiry/thank_you.html')