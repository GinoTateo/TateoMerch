# Generated by Django 4.1.1 on 2023-01-26 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_account_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='region_number',
            field=models.IntegerField(blank=True, default=0, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='account',
            name='route_number',
            field=models.IntegerField(blank=True, default=0, max_length=10, null=True),
        ),
    ]
