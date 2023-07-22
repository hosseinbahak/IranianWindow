# Generated by Django 4.2.3 on 2023-07-11 21:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('connection', models.CharField(default=0, max_length=256)),
                ('registered_date', models.DateField(auto_now_add=True)),
                ('check_date', models.DateField(blank=True, null=True)),
                ('visit', models.BooleanField(default=False)),
                ('sms', models.BooleanField(default=False)),
                ('in_person', models.BooleanField(default=False)),
                ('checkout', models.BooleanField(default=False)),
                ('how_meet', models.CharField(default=0, max_length=256)),
                ('partner', models.BooleanField(default=False)),
                ('state', models.SmallIntegerField(choices=[(0, 'در حال پیگیری'), (1, 'لغو شده'), (2, 'قرارداد بسته شده')], default=0)),
                ('level', models.CharField(default='', max_length=512)),
                ('floor', models.PositiveIntegerField(default=1)),
                ('address', models.CharField(default='', max_length=512)),
                ('region', models.CharField(default='', max_length=256)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee', to=settings.AUTH_USER_MODEL)),
                ('employer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employer_project', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
