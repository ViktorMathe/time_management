# Generated by Django 4.2.2 on 2023-12-08 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clocking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timesheet',
            name='total_worked_hours',
            field=models.CharField(max_length=54, null=True),
        ),
    ]