# Generated by Django 4.2.6 on 2024-03-28 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leave', '0006_leaveapplications_admin_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplications',
            name='attachment',
            field=models.FileField(default='wddadw', upload_to=''),
            preserve_default=False,
        ),
    ]
