# Generated by Django 4.2.7 on 2023-11-12 10:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("job_applications", "0004_alter_jobapplication_date_added_to_database"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="jobapplication",
            name="date_added_to_database",
        ),
    ]