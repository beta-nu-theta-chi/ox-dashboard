# Generated by Django 3.0.7 on 2020-08-28 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_auto_20200827_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brother',
            name='operational_committee',
            field=models.CharField(choices=[('1', 'Membership Development'), ('3', 'Unassigned'), ('0', 'Alumni Relations'), ('2', 'Scholarship')], default='3', max_length=1),
        ),
        migrations.AlterField(
            model_name='brother',
            name='standing_committee',
            field=models.CharField(choices=[('4', 'Unassigned'), ('0', 'Recruitment'), ('3', 'Social'), ('1', 'Public Relations'), ('2', 'Health and Safety')], default='4', max_length=1),
        ),
        migrations.AlterField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(choices=[('6', 'Scholarship'), ('0', 'Recruitment'), ('3', 'Social'), ('5', 'Membership Development'), ('1', 'Public Relations'), ('4', 'Alumni Relations'), ('2', 'Health and Safety')], max_length=1),
        ),
    ]
