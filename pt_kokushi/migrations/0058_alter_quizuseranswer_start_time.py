# Generated by Django 5.0.1 on 2024-02-13 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0057_alter_kokushifield_options_quizuseranswer_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizuseranswer',
            name='start_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
