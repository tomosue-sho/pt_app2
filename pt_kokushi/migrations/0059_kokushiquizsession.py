# Generated by Django 5.0.1 on 2024-02-13 07:48

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0058_alter_quizuseranswer_start_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='KokushiQuizSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='開始時刻')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='終了時刻')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pt_kokushi.exam', verbose_name='試験')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
    ]
