# Generated by Django 5.0.7 on 2024-07-29 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0005_user_fcm_token'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]