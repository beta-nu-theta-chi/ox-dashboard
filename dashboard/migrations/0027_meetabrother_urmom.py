# Generated by Django 3.0.7 on 2020-11-08 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0026_auto_20201011_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetabrother',
            name='urmom',
            field=models.CharField(default='urmom', max_length=3),
        ),
    ]