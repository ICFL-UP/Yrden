import os
import sys
from django.utils import timezone
import kronos

from django.db.models.query import QuerySet

from core.models import Plugin
from core.run import Run


# https://github.com/jgorset/django-kronos
@kronos.register('* * * * *')
def run_plugins():
    plugins: QuerySet[Plugin] = Plugin.objects.get_queryset()

    # set working dir so plugin paths work
    os.chdir(os.path.dirname(sys.argv[0]))

    for plugin in plugins:
        print(f'RUNNING PLUGIN: {plugin.name}')
        should_run = timezone.now() - \
            plugin.last_run_datetime > timezone.timedelta(
                minutes=plugin.interval)

        if should_run:
            run = Run(plugin)
            run.start()
