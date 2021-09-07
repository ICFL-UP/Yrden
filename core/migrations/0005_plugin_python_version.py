# Generated by Django 3.2.6 on 2021-09-07 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210907_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='python_version',
            field=models.CharField(choices=[(0, '/bin/python3.8'), (1, '/bin/python2.7')], default='/bin/python3.8', max_length=15),
            preserve_default=False,
        ),
    ]
