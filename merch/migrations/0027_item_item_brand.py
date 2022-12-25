# Generated by Django 4.1.1 on 2022-12-25 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0026_alter_item_item_size_alter_item_item_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='item_brand',
            field=models.CharField(choices=[('P', 'Peets'), ('I', 'Intelligentsia'), ('S', 'Stumptown')], default='P', max_length=25),
        ),
    ]
