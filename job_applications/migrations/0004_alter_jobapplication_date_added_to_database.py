# Generated by Django 4.2.7 on 2023-11-12 10:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("job_applications", "0003_alter_jobapplication_date_added_to_database"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="date_added_to_database",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
