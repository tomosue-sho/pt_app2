# Generated by Django 4.2 on 2023-12-31 10:38

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0004_customuser_date_joined_customuser_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='date_joined',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='登録日'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='school_year',
            field=models.IntegerField(blank=True, verbose_name='学年'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'その名前はすでに使われています'}, max_length=20, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='名前'),
        ),
    ]