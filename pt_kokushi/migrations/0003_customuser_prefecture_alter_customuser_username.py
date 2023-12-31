# Generated by Django 4.2 on 2023-12-28 09:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0002_customuser_date_of_birth_customuser_school_year_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='prefecture',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='都道府県'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(5), django.core.validators.RegexValidator('^[a-zA-Z0-9]*$')], verbose_name='username'),
        ),
    ]
