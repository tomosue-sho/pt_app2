# Generated by Django 5.0.1 on 2024-01-27 05:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0028_sub2field'),
    ]

    operations = [
        migrations.AddField(
            model_name='sub2field',
            name='subfield',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='sub2fields', to='pt_kokushi.subfield'),
            preserve_default=False,
        ),
    ]
