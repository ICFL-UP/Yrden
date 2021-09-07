# Generated by Django 3.2.6 on 2021-09-07 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_plugin_python_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plugin',
            name='python_version',
            field=models.CharField(choices=[(0, '/bin/python3.8'), (1, '/bin/python2.7')], default='/bin/python', max_length=15),
        ),
    ]
