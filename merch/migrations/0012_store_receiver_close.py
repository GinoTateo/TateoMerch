# Generated by Django 4.1.1 on 2023-01-10 19:08

from django.db import migrations, models
import merch.models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0011_store_receiver_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='receiver_close',
            field=models.TimeField(default=merch.models.default_start_time),
        ),
    ]
