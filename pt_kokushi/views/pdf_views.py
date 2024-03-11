from django.shortcuts import render, redirect, get_object_or_404
from pt_kokushi.forms.pdf_forms import PDFUploadForm
from pt_kokushi.models.pdf_models import PDFDocument, PDFCategory

def pdf_list(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pdf_list')
    else:
        form = PDFUploadForm()

    # カテゴリごとにドキュメントをグルーピング
    categories = PDFCategory.objects.prefetch_related('pdfs')
    category_docs = {cat.name: cat.pdfs.all() for cat in categories}

    return render(request, 'pdf/pdf_list.html', {
        'category_docs': category_docs,
        'form': form
    })
