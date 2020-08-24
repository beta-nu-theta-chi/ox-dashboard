# Generated by Django 3.0.7 on 2020-08-23 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20200823_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='operational_committee',
            field=models.CharField(choices=[('1', 'Membership Development'), ('2', 'Scholarship'), ('3', 'Unassigned'), ('0', 'Alumni Relations')], default='3', max_length=1),
        ),
        migrations.AlterField(
            model_name='brother',
            name='standing_committee',
            field=models.CharField(choices=[('0', 'Recruitment'), ('2', 'Health and Safety'), ('4', 'Unassigned'), ('1', 'Public Relations'), ('3', 'Social')], default='4', max_length=1),
        ),
        migrations.AlterField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(choices=[('0', 'Recruitment'), ('2', 'Health and Safety'), ('1', 'Public Relations'), ('5', 'Membership Development'), ('6', 'Scholarship'), ('4', 'Alumni Relations'), ('3', 'Social')], max_length=1),
        ),
    ]