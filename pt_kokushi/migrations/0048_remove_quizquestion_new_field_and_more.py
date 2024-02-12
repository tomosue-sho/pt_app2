# Generated by Django 4.2 on 2024-02-12 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0047_quizquestion_new_field_alter_quizquestion_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quizquestion',
            name='new_field',
        ),
        migrations.AlterField(
            model_name='quizquestion',
            name='field',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='分野'),
        ),
    ]
