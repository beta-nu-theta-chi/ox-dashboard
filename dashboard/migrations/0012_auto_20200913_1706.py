# Generated by Django 3.0.7 on 2020-09-13 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20200913_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='committeemeetingevent',
            name='recurring',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='brother',
            name='pronouns',
            field=models.CharField(blank=True, choices=[('FEM', 'she/her/hers'), ('MASC', 'he/him/his'), ('NON', 'they/them/theirs')], max_length=30),
        ),
        migrations.AlterField(
            model_name='position',
            name='title',
            field=models.CharField(choices=[('President', 'President'), ('Vice President', 'Vice President'), ('Vice President of Health and Safety', 'Vice President Of Health And Safety'), ('Secretary', 'Secretary'), ('Treasurer', 'Treasurer'), ('Marshal', 'Marshal'), ('Recruitment Chair', 'Recruitment Chair'), ('Scholarship Chair', 'Scholarship Chair'), ('Detail Manager', 'Detail Manager'), ('Philanthropy Chair', 'Philanthropy Chair'), ('Public Relations Chair', 'Public Relations Chair'), ('Service Chair', 'Service Chair'), ('Alumni Relations Chair', 'Alumni Relations Chair'), ('Membership Development Chair', 'Membership Development Chair'), ('Social Chair', 'Social Chair'), ('Adviser', 'Adviser')], max_length=45, unique=True),
        ),
    ]
