# Generated by Django 5.0.1 on 2024-01-22 12:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0014_comment_nickname_alter_comment_author_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='nickname',
            field=models.CharField(default=1, max_length=20, verbose_name='ニックネーム'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='投稿者'),
        ),
    ]
