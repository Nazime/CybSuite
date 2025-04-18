# Generated by Django 5.0.3 on 2025-04-12 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cybsmodels", "0002_run_control_latest_run"),
    ]

    operations = [
        migrations.AddField(
            model_name="run",
            name="status",
            field=models.TextField(
                blank=True,
                choices=[
                    ("created", "created"),
                    ("finished", "finished"),
                    ("error", "error"),
                    ("running", "running"),
                    ("cancelled", "cancelled"),
                ],
                null=True,
            ),
        ),
    ]
