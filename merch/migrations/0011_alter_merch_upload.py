# Generated by Django 4.1.1 on 2022-11-17 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0010_alter_merch_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merch',
            name='upload',
            field=models.ImageField(default='N/A', height_field=100, upload_to='images/', width_field=100),
        ),
    ]
