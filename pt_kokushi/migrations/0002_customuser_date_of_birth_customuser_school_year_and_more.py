# Generated by Django 4.2 on 2023-12-26 04:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True, verbose_name='誕生日'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='school_year',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customuser',
            name='username',
            field=models.CharField(default=2, max_length=10, unique=True, validators=[django.core.validators.MinLengthValidator(5), django.core.validators.RegexValidator('^[a-zA-Z0-9]*$')], verbose_name='username'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
    ]
