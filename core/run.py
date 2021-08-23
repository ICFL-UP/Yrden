import os
import threading
import subprocess
import datetime
import logging

from django.utils.timezone import make_aware

from core.models import Plugin, PluginRun
from core.utils import datetime_to_string

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class Run(threading.Thread):
    def __init__(self, plugin: Plugin) -> None:
        logging.debug('Creating Run')
        self.plugin_run = PluginRun()
        self.plugin_run.plugin = plugin
        threading.Thread.__init__(self)

    def run(self):
        logging.debug(f'Running Plugin: {self.plugin_run.plugin.name}')

        main = self.plugin_run.plugin.plugin_dest + os.sep + 'main.py'
        python = self.plugin_run.plugin.plugin_dest + os.sep + \
            '.venv' + os.sep + 'bin' + os.sep + 'python'

        # TODO: set status to HF if hash validation fails
        try:
            start_time = make_aware(datetime.datetime.now())
            self.plugin_run.plugin.last_run_datetime = start_time
            self.plugin_run.plugin.save()

            self.plugin_run.execute_start_time = start_time

            completedProcess: subprocess.CompletedProcess = subprocess.run(
                [python, main],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=300,  # 5 minutes
            )

            end_time = make_aware(datetime.datetime.now())

            self.plugin_run.run_status = PluginRun.RunStatus.SUCCESS
            self.plugin_run.stdout = completedProcess.stdout
            self.plugin_run.stderr = completedProcess.stderr
            self.plugin_run.execute_duration = end_time - start_time
        except subprocess.TimeoutExpired as te:
            self.plugin_run.run_status = PluginRun.RunStatus.TIMED_OUT
            self.plugin_run.stdout = te.stdout
            self.plugin_run.stderr = te.stderr
        except subprocess.CalledProcessError as cpe:
            self.plugin_run.run_status = PluginRun.RunStatus.FAILED
            self.plugin_run.stdout = cpe.stdout
            self.plugin_run.stderr = cpe.stderr

        self.plugin_run.save()

        logging.debug(
            f'Run Finished: {self.plugin_run.stdout}, {self.plugin_run.stderr}, {datetime_to_string(self.plugin_run.execute_start_time)}, ${self.plugin_run.execute_duration}')
