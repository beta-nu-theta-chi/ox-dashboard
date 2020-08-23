# Generated by Django 3.1 on 2020-08-23 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20200823_1242'),
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
            field=models.CharField(choices=[('4', 'Unassigned'), ('0', 'Recruitment'), ('1', 'Public Relations'), ('2', 'Health and Safety'), ('3', 'Social')], default='4', max_length=1),
        ),
        migrations.AlterField(
            model_name='committeemeetingevent',
            name='committee',
            field=models.CharField(choices=[('0', 'Recruitment'), ('6', 'Scholarship'), ('1', 'Public Relations'), ('5', 'Membership Development'), ('2', 'Health and Safety'), ('3', 'Social'), ('4', 'Alumni Relations')], max_length=1),
        ),
    ]
