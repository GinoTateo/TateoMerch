# Generated by Django 3.2.16 on 2023-05-01 21:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operations', '0007_alter_warehouse_inventory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventory',
            old_name='last_inventory',
            new_name='date',
        ),
    ]
