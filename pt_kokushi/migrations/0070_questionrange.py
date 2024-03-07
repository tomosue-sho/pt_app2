# Generated by Django 4.2 on 2024-03-07 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0069_choiceexplanation'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_id', models.IntegerField(verbose_name='開始ID')),
                ('end_id', models.IntegerField(verbose_name='終了ID')),
                ('exam', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pt_kokushi.exam', verbose_name='年度')),
            ],
            options={
                'verbose_name': '国試「問題ID範囲」',
                'verbose_name_plural': '国試「問題ID範囲」',
            },
        ),
    ]
