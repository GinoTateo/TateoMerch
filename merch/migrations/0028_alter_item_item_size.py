# Generated by Django 4.1.1 on 2022-12-25 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0027_item_item_brand'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='item_size',
            field=models.CharField(choices=[('18', '18oz'), ('10.5', '10.5oz')], max_length=25),
        ),
    ]
