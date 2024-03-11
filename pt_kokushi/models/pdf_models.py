from django.db import models

class PDFCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
def get_default_category():
    category, _ = PDFCategory.objects.get_or_create(name='整形外科')
    return category.id

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(PDFCategory, on_delete=models.CASCADE, related_name='pdfs', null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.category:
            default_category, _ = PDFCategory.objects.get_or_create(name='整形外科')
            self.category = default_category
        super(PDFDocument, self).save(*args, **kwargs)