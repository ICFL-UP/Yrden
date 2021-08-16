# Generated by Django 3.2.6 on 2021-08-16 18:22

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Plugin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('interval', models.PositiveIntegerField(default=5, validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(60)])),
                ('last_run_datetime', models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0))),
                ('should_run', models.BooleanField(default=True)),
                ('plugin_dest', models.CharField(default='undefined', max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='PluginSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_dest', models.CharField(default='undefined', max_length=1000)),
                ('source_hash', models.CharField(default='undefined', max_length=512)),
                ('upload_time', models.DateTimeField(default=datetime.datetime(1900, 1, 1, 0, 0))),
                ('upload_user', models.CharField(default='undefined', max_length=200)),
                ('source_file_hash', jsonfield.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='PluginRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stdout', models.TextField()),
                ('stderr', models.TextField()),
                ('execute_start_time', models.DateTimeField()),
                ('execute_duration', models.DurationField()),
                ('run_status', models.CharField(choices=[('FA', 'Failed'), ('HF', 'Hash Failed'), ('SU', 'Success'), ('TO', 'Timed Out')], default='SU', max_length=2)),
                ('plugin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.plugin')),
            ],
        ),
        migrations.AddField(
            model_name='plugin',
            name='plugin_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.pluginsource'),
        ),
    ]
