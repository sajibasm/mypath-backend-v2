# Generated by Django 4.2.9 on 2025-05-26 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("device", "0003_init_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="sensordata",
            name="session_id",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
