# Generated by Django 4.2.2 on 2023-08-18 14:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('manager', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Timesheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_datetime', models.DateTimeField(auto_now_add=True)),
                ('clocking_time', models.DateTimeField(null=True)),
                ('logging', models.CharField(choices=[('IN', 'In'), ('OUT', 'Out')], max_length=3)),
                ('ip_address', models.GenericIPAddressField(null=True)),
                ('comments', models.TextField(blank=True, null=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.business')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_employee', to=settings.AUTH_USER_MODEL)),
                ('recorded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_recorded_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'clocking_time',
            },
        ),
    ]
