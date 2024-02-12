# Generated by Django 5.0.1 on 2024-02-12 11:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0055_delete_kokushifield'),
    ]

    operations = [
        migrations.CreateModel(
            name='KokushiField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='分野名')),
            ],
            options={
                'verbose_name': '分野',
                'verbose_name_plural': '分野',
            },
        ),
        migrations.AddField(
            model_name='quizquestion',
            name='field',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pt_kokushi.kokushifield', verbose_name='分野'),
        ),
    ]
