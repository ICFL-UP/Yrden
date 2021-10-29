import os
import threading
import subprocess
import logging

from django.conf import settings
from django.utils import timezone

from core.models import Plugin, PluginRun
from core.utils import datetime_to_string, run_subprocess, validate_plugin_hash
from core.exceptions import HashJSONFailedException
from core.enums.run_status import RunStatus

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class Run(threading.Thread):
    def __init__(self, plugin: Plugin) -> None:
        logging.debug('Creating Run')
        self.plugin_run = PluginRun()
        self.plugin_run.plugin = plugin
        threading.Thread.__init__(self)

    def run(self):
        logging.debug(f'Running Plugin: {self.plugin_run.plugin.plugin_name}')

        main = self.plugin_run.plugin.plugin_dest + os.sep + 'main.py'
        python = self.plugin_run.plugin.plugin_dest + os.sep + \
            '.venv' + os.sep + 'bin' + os.sep + 'python'
        if os.name == 'nt':
            python = self.plugin_run.plugin.plugin_dest + os.sep + \
            '.venv' + os.sep + 'Scripts' + os.sep + 'python'

        try:
            start_time = timezone.now()
            self.plugin_run.plugin.last_run_datetime = start_time
            self.plugin_run.plugin.save()

            validate_plugin_hash(self.plugin_run.plugin)

            self.plugin_run.execute_start_time = start_time

            command = [
                python,
                main
            ]
            cwd = os.getcwd() + os.sep + self.plugin_run.plugin.plugin_dest
            completedProcess: subprocess.CompletedProcess = run_subprocess(
                command=command, timeout=settings.PLUGIN_RUN_TIMEOUT, shell=True, cwd=cwd)

            end_time = timezone.now()

            self.plugin_run.run_status = RunStatus.SUCCESS
            self.plugin_run.stdout = completedProcess.stdout.decode('utf-8')
            self.plugin_run.stderr = completedProcess.stderr.decode('utf-8')
            self.plugin_run.execute_duration = end_time - start_time
        except subprocess.TimeoutExpired as te:
            self.plugin_run.run_status = RunStatus.TIMED_OUT
            self.plugin_run.stdout = te.stdout.decode('utf-8')
            self.plugin_run.stderr = te.stderr.decode('utf-8')
        except subprocess.CalledProcessError as cpe:
            self.plugin_run.run_status = RunStatus.FAILED
            self.plugin_run.stdout = cpe.stdout.decode('utf-8')
            self.plugin_run.stderr = cpe.stderr.decode('utf-8')
        except HashJSONFailedException as hf:
            self.plugin_run.run_status = RunStatus.HASH_FAILED
            self.plugin_run.stderr = f'Error {hf}'

        self.plugin_run.save()

        logging.debug(
            f'Run Finished: {self.plugin_run.stdout}, {self.plugin_run.stderr}, {datetime_to_string(self.plugin_run.execute_start_time)}, ${self.plugin_run.execute_duration}')
