# Generated by Django 4.2.3 on 2023-07-21 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0015_alter_project_check_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='immediate',
            new_name='advice',
        ),
    ]