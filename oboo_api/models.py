import shutil
from datetime import date, datetime, timedelta

from django.db import models
from django.utils import timezone
from django.utils.timezone import localtime, make_aware, is_naive

from oboo_api.hpfetch import CALENDARS_DIRECTORY, download_calendars, get_events_of_day


class Building(models.Model):
    """
    A class representing a physical building of ISEP.
    """
    name = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField("Creation timestamp")

    def __str__(self):
        return f'{self.name}'
