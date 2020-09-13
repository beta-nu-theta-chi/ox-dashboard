# Generated by Django 3.0.7 on 2020-08-24 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20200823_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='operational_committee',
            field=models.CharField(choices=[('1', 'Membership Development'), ('2', 'Scholarship'), ('0', 'Alumni Relations'), ('3', 'Unassigned')], default='3', max_length=1),
        ),
        migrations.AlterField(
            model_name='brother',
            name='standing_committee',
            field=models.CharField(choices=[('1', 'Public Relations'), ('3', 'Social'), ('0', 'Recruitment'), ('2', 'Health and Safety'), ('4', 'Unassigned')], default='4', max_length=1),
        ),
        migrations.AlterField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(choices=[('1', 'Public Relations'), ('6', 'Scholarship'), ('3', 'Social'), ('0', 'Recruitment'), ('2', 'Health and Safety'), ('4', 'Alumni Relations'), ('5', 'Membership Development')], max_length=1),
        ),
    ]
