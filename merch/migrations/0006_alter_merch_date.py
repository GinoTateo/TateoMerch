# Generated by Django 4.1.1 on 2022-11-15 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0005_merch_case_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merch',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
