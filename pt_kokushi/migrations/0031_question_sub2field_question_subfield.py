# Generated by Django 5.0.1 on 2024-01-27 07:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0030_subfield_has_detailed_selection'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='sub2field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='pt_kokushi.sub2field'),
        ),
        migrations.AddField(
            model_name='question',
            name='subfield',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questions', to='pt_kokushi.subfield'),
        ),
    ]
