# Generated by Django 3.0.7 on 2020-10-11 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_auto_20201011_1808'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='classes',
            name='number_constraint',
        ),
        migrations.AlterField(
            model_name='classes',
            name='number',
            field=models.CharField(max_length=4),
        ),
    ]