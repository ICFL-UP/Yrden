import os
import sys
import datetime
import kronos

from django.db.models.query import QuerySet
from django.utils.timezone import make_aware

from core.models import Plugin
from core.run import Run


@kronos.register('* * * * *')
def run_plugins():
    plugins: QuerySet[Plugin] = Plugin.objects.get_queryset()

    # set working dir so plugin paths work
    os.chdir(os.path.dirname(sys.argv[0]))

    for plugin in plugins:
        print(f'RUNNING PLUGIN: {plugin.name}')
        should_run = make_aware(datetime.datetime.now()
                                ) - plugin.last_run_datetime > datetime.timedelta(minutes=plugin.interval)

        if should_run:
            run = Run(plugin)
            run.start()
