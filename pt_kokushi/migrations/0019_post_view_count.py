# Generated by Django 5.0.1 on 2024-01-23 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0018_post_last_commented_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='view_count',
            field=models.PositiveIntegerField(default=0, verbose_name='ビュー数'),
        ),
    ]
