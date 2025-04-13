# Generated by Django 5.0.3 on 2025-04-13 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cybsmodels", "0003_run_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="control",
            name="severity",
            field=models.TextField(
                blank=True,
                choices=[
                    ("undefined", "undefined"),
                    ("info", "info"),
                    ("low", "low"),
                    ("medium", "medium"),
                    ("high", "high"),
                    ("critical", "critical"),
                ],
                null=True,
            ),
        ),
    ]
