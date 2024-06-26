# Generated by Django 5.0.3 on 2024-03-26 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_user_gender_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='dept',
            field=models.CharField(blank=True, choices=[('COMPUTER', 'Computer'), ('COMMERCE', 'Commerce'), ('PHYSICS', 'Physics')], max_length=50),
        ),
        migrations.AddField(
            model_name='user',
            name='emp_code',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
