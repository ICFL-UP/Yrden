from jsonfield import JSONField
from typing import Any

from django.db.models.query import QuerySet
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.conf import settings

from core.enums.plugin_status import PluginStatus
from core.enums.run_status import RunStatus


class SoftDeletionQuerySet(QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeletionManager(models.Manager):
    ''' Use this manager to get objects that have a deleted field '''

    def __init__(self, *args, **kwargs) -> None:
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)

        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()


class PluginSource(SoftDeletionModel):

    # destination of source files
    source_dest: str = models.CharField(max_length=1000, null=False)

    # hash of source zip
    source_hash: str = models.CharField(max_length=512, null=False)

    # time the source was uploaded to the system
    upload_time: timezone = models.DateTimeField(null=False)

    # name of the user that uploaded the file
    upload_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    # json string of source file hashes
    source_file_hash: dict = JSONField()

    def __str__(self) -> str:
        return self.source_hash


class Plugin(SoftDeletionModel):

    plugin_source: PluginSource = models.OneToOneField(
        PluginSource, on_delete=models.CASCADE)

    # name of the plugin
    plugin_name: str = models.CharField(max_length=200, null=False)

    # interval for when the plugin should run
    interval: int = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(5), MaxValueValidator(60)])

    # last time the plugin ran
    last_run_datetime: timezone = models.DateTimeField(
        default=timezone.now().replace(year=1900, month=1, day=1, hour=0, minute=0, second=0, microsecond=0))

    # should the plugin run or not
    should_run: bool = models.BooleanField(default=True)

    # plugin destination
    plugin_dest: str = models.CharField(max_length=1000, null=False)

    # status of plugin
    status: str = models.CharField(max_length=11, choices=[
                                   (tag.name, tag.value) for tag in PluginStatus], null=True)

    # python_version
    python_version: str = models.CharField(max_length=15)

    # stdout of the subprocess run
    stdout: str = models.TextField(null=True)

    # stderr of the subprocess run
    stderr: str = models.TextField(null=True)

    def __str__(self) -> str:
        return self.plugin_source.source_hash + '_' + self.plugin_name

    def delete(self):
        self.plugin_source.delete()
        return super().delete()

    def hard_delete(self):
        self.plugin_source.hard_delete()
        return super().hard_delete()


class PluginRun(SoftDeletionModel):

    # Foreing key to the Plugin
    plugin: Plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)

    # stdout of the subprocess run
    stdout: str = models.TextField(null=True)

    # stderr of the subprocess run
    stderr: str = models.TextField(null=True)

    # start time of the run
    execute_start_time: timezone = models.DateTimeField()

    # duration of the run
    execute_duration = models.DurationField(null=True)

    # status of the run
    run_status: str = models.CharField(
        max_length=11, choices=[(tag.name, tag.value) for tag in RunStatus], default=RunStatus.SUCCESS)

    def __str__(self) -> str:
        return self.plugin.plugin_source.source_hash + '_' + str(self.execute_start_time)

    def delete(self):
        self.plugin.delete()
        return super().delete()

    def hard_delete(self):
        self.plugin.hard_delete()
        return super().hard_delete()
