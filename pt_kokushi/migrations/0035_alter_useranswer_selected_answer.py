# Generated by Django 4.2 on 2024-01-30 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0034_question_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useranswer',
            name='selected_answer',
            field=models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], max_length=1),
        ),
    ]
