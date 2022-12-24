# Generated by Django 4.1.1 on 2022-12-21 03:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merch', '0017_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64, unique=True)),
                ('description', models.TextField(default='')),
                ('cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.DeleteModel(
            name='Item',
        ),
        migrations.DeleteModel(
            name='Order',
        ),
    ]
