# Generated by Django 3.2.6 on 2021-09-07 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_plugin_python_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plugin',
            name='python_version',
            field=models.CharField(max_length=15),
        ),
    ]
