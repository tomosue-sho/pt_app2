# Generated by Django 5.0.1 on 2024-01-23 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0017_alter_comment_nickname_alter_post_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='last_commented_at',
            field=models.DateTimeField(auto_now=True, verbose_name='最終コメント日時'),
        ),
    ]
