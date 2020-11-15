# Generated by Django 3.0.7 on 2020-11-14 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0030_report_is_officer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='position',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='report', to='dashboard.Position'),
        ),
    ]