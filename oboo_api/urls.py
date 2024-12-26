from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("buildings", views.buildings, name="buildings"),
    path("floors", views.floors, name="floors"),
    path("rooms", views.rooms, name="rooms"),
    path("timeslots", views.time_slots, name="time_slots"),
]
