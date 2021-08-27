# Generated by Django 3.2.6 on 2021-08-26 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plugin',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='pluginsource',
            name='deleted',
        ),
        migrations.AddField(
            model_name='plugin',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pluginsource',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
