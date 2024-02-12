# Generated by Django 5.0.1 on 2024-02-12 06:56

from django.db import migrations

def add_initial_kokushifield_data(apps, schema_editor):
    KokushiField = apps.get_model('pt_kokushi', 'KokushiField')
    fields = [
        'MMT',
        '運動学',
        # 他の分野名を追加
    ]
    for field_name in fields:
        KokushiField.objects.create(name=field_name)

class Migration(migrations.Migration):

    dependencies = [
        ('pt_kokushi', '0053_alter_kokushifield_options'),
    ]

    operations = [
        migrations.RunPython(add_initial_kokushifield_data),
    ]
