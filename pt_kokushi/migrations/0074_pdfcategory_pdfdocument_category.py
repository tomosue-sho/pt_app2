# Generated by Django 4.2 on 2024-03-11 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0073_pdfdocument'),
    ]

    operations = [
        migrations.CreateModel(
            name='PDFCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='pdfdocument',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pdfs', to='pt_kokushi.pdfcategory'),
        ),
    ]
