# Generated by Django 5.0.3 on 2024-03-26 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0003_leaveapplications_which_half'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaveapplications',
            name='which_half',
            field=models.CharField(blank=True, choices=[('FIRST_HALF', 'First Half'), ('SECOND_HALF', 'Second Half')], max_length=20, null=True),
        ),
    ]
