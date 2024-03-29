# Generated by Django 5.0.1 on 2024-02-07 04:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0042_bookmark'),
    ]

    operations = [
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice_text', models.CharField(max_length=255, verbose_name='選択肢')),
                ('is_correct', models.BooleanField(default=False, verbose_name='正解')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='pt_kokushi.quizquestion')),
            ],
        ),
        migrations.CreateModel(
            name='QuizUserAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answered_at', models.DateTimeField(auto_now_add=True, verbose_name='回答日時')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pt_kokushi.quizquestion', verbose_name='問題')),
                ('selected_choices', models.ManyToManyField(to='pt_kokushi.choice', verbose_name='選んだ選択肢')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
        ),
    ]
