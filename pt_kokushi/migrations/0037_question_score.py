# Generated by Django 4.2 on 2024-02-01 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0036_useranswer_is_correct'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='score',
            field=models.IntegerField(default=1),
        ),
    ]
