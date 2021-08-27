import logging
from typing import Any, Optional

from django.db.models.query import QuerySet
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Plugin
from core.run import Run

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        plugins: QuerySet[Plugin] = Plugin.objects.get_queryset()
        for plugin in plugins:
            should_run = timezone.now() - \
                plugin.last_run_datetime > timezone.timedelta(
                    minutes=plugin.interval)

            if should_run:
                run = Run(plugin)
                run.start()
