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
    long_name = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    created_at = models.DateTimeField("Creation timestamp")

    def __str__(self):
        return f'{self.name}'


class Floor(models.Model):
    """
    A class representing a physical floor of a :py:class:`Building`.
    """
    number = models.IntegerField("Floor number")
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField("Creation timestamp")
    building = models.ForeignKey(Building, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.building}, {self.number})'

    class Meta:
        # A Building can't have two (or more) floors with the same number
        unique_together = ("number", "building")


class Room(models.Model):
    """
    A class representing a physical room of a :py:class:`Floor`.
    """
    number = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=64)
    created_at = models.DateTimeField("Creation timestamp")
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.number} ({self.name})'


class TimeSlot(models.Model):
    """
    A class representing a time slot in the planning of a :py:class:`Room`.
    """
    # These variables define the boundaries of the schedule displayed for each room
    DAY_START = datetime(2000, 1, 1, 8, 0, 0, 0)
    DAY_END = datetime(2000, 1, 1, 20, 0, 0, 0)

    subject = models.CharField(max_length=512, verbose_name="Subject name")
    start_time = models.DateTimeField("Start time")
    end_time = models.DateTimeField("End time")
    created_at = models.DateTimeField("Creation timestamp")
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.room.number}] {localtime(self.start_time).strftime("%d/%m/%Y, %H:%M")} - {localtime(self.end_time).strftime("%H:%M")} | {self.subject}'

    @staticmethod
    def update_time_slots() -> None:
        """
        Deletes all stored calendars and time slots and forces the re-download of calendars.
        New :py:class:`TimeSlot` objects are created from the newly downloaded calendars.
        """
        # Delete all the calendars to force re-download
        shutil.rmtree(CALENDARS_DIRECTORY, ignore_errors=True)

        # Fetch all the room numbers from the DB and download all calendars
        room_numbers = Room.objects.values_list("number", flat=True)
        download_calendars(room_numbers)

        # Delete all time slots to ensure there are no duplicates
        TimeSlot.objects.all().delete()

        all_time_slots_created = True
        for room_number in room_numbers:
            print(f'Creating time slots for room {room_number}...', end="", flush=True)

            # If the room does not exist in the application, skip it
            try:
                room = Room.objects.get(number=room_number)
            except Room.DoesNotExist:
                continue

            try:
                events = get_events_of_day(room_number, date.today())
            except Exception:
                all_time_slots_created = False
                print("\t[FAILED]")
            else:
                for event in events:
                    # Extract the three values from the tuple
                    # All naive datetime objects are converted to aware datetime objects
                    start_datetime, end_datetime, subject = make_aware(event[0]) if is_naive(event[0]) else event[0], make_aware(event[1]) if is_naive(event[1]) else event[1], event[2]
                    room.timeslot_set.create(subject=subject, start_time=start_datetime, end_time=end_datetime, created_at=timezone.now())
                print("\t[OK]")

        if all_time_slots_created:
            print("All time slots have been successfully created.")
        else:
            print("[WARN] Some time slots could not be created (some room calendars may be missing).")


class OTP(models.Model):
    """
    A class representing a One Time Password.
    """
    code = models.CharField(max_length=6)
    email = models.CharField(max_length=64)
    created_at = models.DateTimeField("Creation timestamp")
    expiration = models.DateTimeField("Expiration date")

    def __str__(self):
        return f'[OTP: {self.code} ({self.email})]'


class APIKey(models.Model):
    """
    A class representing an API Key.
    """
    key = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    created_at = models.DateTimeField("Creation timestamp")
    expiration = models.DateTimeField("Expiration date")

    def __str__(self):
        return f'[APIKey: {self.key} ({self.email})]'

# This is stupid, but there is no way to make django-crontab call a static method from a class (the function to call must not be in a class)
# This is due to the way django-crontab parses the settings.CRONJOBS list, see: https://github.com/kraiz/django-crontab/blob/master/django_crontab/crontab.py#L169-L172
def update_time_slots():
    TimeSlot.update_time_slots()
