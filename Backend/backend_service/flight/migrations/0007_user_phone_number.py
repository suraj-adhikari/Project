# Generated by Django 5.0.7 on 2024-07-29 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0006_delete_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.SmallIntegerField(blank=True, max_length=13, null=True),
        ),
    ]
