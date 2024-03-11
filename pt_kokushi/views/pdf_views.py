from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from pt_kokushi.forms.pdf_forms import PDFUploadForm
from pt_kokushi.models.pdf_models import PDFDocument,PDFCategory

def pdf_list(request, category_id=None):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pdf_list')
    else:
        form = PDFUploadForm()

    if category_id:
        category = get_object_or_404(PDFCategory, id=category_id)
        documents = category.pdfs.all()
    else:
        category = None
        documents = PDFDocument.objects.all()

    return render(request, 'pdf/pdf_list.html', {
        'category': category,
        'documents': documents,
        'form': form
    })