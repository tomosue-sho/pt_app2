# Generated by Django 5.0.1 on 2024-01-28 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0031_question_sub2field_question_subfield'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='field',
        ),
        migrations.AddField(
            model_name='question',
            name='choice1',
            field=models.CharField(default='No choice', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='choice2',
            field=models.CharField(default='No choice', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='choice3',
            field=models.CharField(default='No choice', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='question',
            name='choice4',
            field=models.CharField(default='No choice', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='question',
            name='correct_answer',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], max_length=1),
        ),
    ]
