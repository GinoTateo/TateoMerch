# Generated by Django 3.2.16 on 2023-07-20 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0004_storelistitem'),
        ('operations', '0012_auto_20230719_1728'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warehouse',
            name='routes',
        ),
        migrations.AddField(
            model_name='warehouse',
            name='routes',
            field=models.ManyToManyField(blank=True, null=True, to='rsr.Route'),
        ),
    ]
