# Generated by Django 5.0.3 on 2024-03-26 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0004_alter_leaveapplications_which_half'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeleaves',
            name='leaves_remaining',
            field=models.DecimalField(decimal_places=1, max_digits=5),
        ),
    ]