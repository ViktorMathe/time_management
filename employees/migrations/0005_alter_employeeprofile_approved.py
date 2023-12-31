# Generated by Django 4.2.2 on 2023-08-24 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_alter_employeeprofile_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeprofile',
            name='approved',
            field=models.BooleanField(choices=[(0, 'Pending'), (1, 'Approved')], default=0),
        ),
    ]
