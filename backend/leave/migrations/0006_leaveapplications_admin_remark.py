# Generated by Django 5.0.3 on 2024-03-26 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0005_alter_employeeleaves_leaves_remaining'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplications',
            name='admin_remark',
            field=models.TextField(blank=True),
        ),
    ]