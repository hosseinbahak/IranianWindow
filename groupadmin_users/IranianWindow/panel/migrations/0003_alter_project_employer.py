# Generated by Django 4.2.3 on 2023-07-11 21:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('panel', '0002_alter_project_connection_alter_project_how_meet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='employer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employer', to=settings.AUTH_USER_MODEL),
        ),
    ]
