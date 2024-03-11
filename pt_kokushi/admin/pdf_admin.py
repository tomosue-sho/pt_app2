from django.contrib import admin
from pt_kokushi.models.pdf_models import PDFDocument,PDFCategory

@admin.register(PDFDocument)
class PDFDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at')
    
admin.site.register(PDFCategory)