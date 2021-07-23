import datetime

from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator


class Plugin(models.Model):
    name = models.CharField(max_length=200)
    interval = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(5), MaxValueValidator(60)])
    last_run_datetime = models.DateTimeField(
        default=datetime.datetime(1900, 1, 1, 0, 0, 0))
    should_run = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self):
        return reverse('core:detail', args=[self.id])
