# Generated by Django 4.2 on 2024-01-13 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0008_alter_customuser_school_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='date_of_birth',
            new_name='birth_of_date',
        ),
        migrations.RemoveField(
            model_name='customuser',
            name='birth_date',
        ),
    ]
