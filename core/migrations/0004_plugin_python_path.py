# Generated by Django 3.2.6 on 2021-08-08 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210807_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='plugin',
            name='python_path',
            field=models.CharField(default='undefined', max_length=1000),
        ),
    ]
