import logging
from typing import Any, Optional

from django.db.models.query import QuerySet
from django.core.management.base import BaseCommand

from core.models import Plugin
from core.utils import validate_plugin_hash
from core.exceptions import HashJSONFailedException

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        plugins: QuerySet[Plugin] = Plugin.objects.get_queryset()

        for plugin in plugins:
            try:
                validate_plugin_hash(plugin)
            except HashJSONFailedException as hf:
                logging.error(f'Error {hf}')
