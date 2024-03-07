# Generated by Django 4.2 on 2024-03-05 09:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0066_column'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'verbose_name': '休憩室コラム', 'verbose_name_plural': '休憩室コラム'},
        ),
        migrations.CreateModel(
            name='ExplanationImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to='explanation_images/', verbose_name='解説画像')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='explanation_images', to='pt_kokushi.quizquestion', verbose_name='問題')),
            ],
        ),
    ]