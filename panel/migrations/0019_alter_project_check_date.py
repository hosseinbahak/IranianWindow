# Generated by Django 4.2.3 on 2023-07-21 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0018_alter_project_floor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='check_date',
            field=models.DateTimeField(default=None),
        ),
    ]