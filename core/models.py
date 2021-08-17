import datetime

from django.db import models
from django.utils.timezone import make_aware
from jsonfield import JSONField
from django.core.validators import MaxValueValidator, MinValueValidator


class PluginSource(models.Model):

    # destination of source files
    source_dest: str = models.CharField(max_length=1000, null=False)

    # hash of source zip
    source_hash: str = models.CharField(max_length=512, null=False)

    # time the source was uploaded to the system
    upload_time: datetime.datetime = models.DateTimeField(null=False)

    # name of the user that uploaded the file
    upload_user: str = models.CharField(max_length=200, null=False)

    # json string of source file hashes
    source_file_hash: dict = JSONField()

    def __str__(self) -> str:
        return self.source_hash


class Plugin(models.Model):
    plugin_source: PluginSource = models.OneToOneField(PluginSource, on_delete=models.CASCADE)

    # name of the plugin
    name: str = models.CharField(max_length=200, null=False)
    
    # interval for when the plugin should run
    interval: int = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(5), MaxValueValidator(60)])
    
    # last time the plugin ran
    last_run_datetime: datetime.datetime = models.DateTimeField(
        default=make_aware(datetime.datetime(1900, 1, 1, 0, 0, 0)))
    
    # should the plugin run or not
    should_run: bool = models.BooleanField(default=True)
    
    # plugin destination
    plugin_dest: str = models.CharField(max_length=1000, null=False)

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs):
        self.plugin_source.delete()
        return super(self.__class__, self).delete(*args, **kwargs)


class PluginRun(models.Model):

    class RunStatus(models.TextChoices):
        FAILED = 'FA'
        HASH_FAILED = 'HF'
        SUCCESS = 'SU'
        TIMED_OUT = 'TO'

    # Foreing key to the Plugin
    plugin: Plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)
    
    # stdout of the subprocess run
    stdout = models.TextField()

    # stderr of the subprocess run
    stderr = models.TextField()

    # start time of the run
    execute_start_time: datetime.datetime = models.DateTimeField()
    
    # duration of the run
    execute_duration = models.DurationField()
    
    # status of the run
    run_status = models.CharField(max_length=2, choices=RunStatus.choices, default=RunStatus.SUCCESS)

    def __str__(self) -> str:
        return self.plugin.plugin_source.source_hash + '_' + self.execute_start_time
