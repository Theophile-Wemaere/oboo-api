from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse

from .models import Building, Floor, Room, TimeSlot

from .authfunc import handle_otp


def index(request):
    return HttpResponse("Hello, world. You're at the Oboo API index.")

def buildings(request):
    buildings = Building.objects.all()
    buildings_dicts = [model_to_dict(building, fields=('id', 'name', 'long_name', 'city')) for building in buildings]
    return JsonResponse(buildings_dicts, safe=False)

def floors(request):
    floors = Floor.objects.all()
    floors_dicts = [model_to_dict(floor, fields=('id', 'number', 'name', 'building')) for floor in floors]
    return JsonResponse(floors_dicts, safe=False)

def rooms(request):
    rooms = Room.objects.all()
    rooms_dicts = [model_to_dict(room, fields=('id', 'number', 'name', 'floor')) for room in rooms]
    return JsonResponse(rooms_dicts, safe=False)

def time_slots(request):
    time_slots = TimeSlot.objects.all()
    time_slots_dicts = [model_to_dict(time_slot, fields=('id', 'subject', 'start_time', 'end_time', 'room')) for time_slot in time_slots]
    return JsonResponse(time_slots_dicts, safe=False)

def send_otp(request):
    """
    send OTP to email address in GET parameter 'email'
    """

    receiver = request.GET.get('email', None)
    if receiver is None:
        return JsonResponse({
            "status":"missing_parameter"
        })


    otp,status = handle_otp(receiver)
    if status == 0:
        return JsonResponse({
            "status":"success"
        })
    elif status == -1:
        return JsonResponse({
            "status":"not_isep_email"
        })
    elif status == -2:
        return JsonResponse({
            "status":"bad_emails"
        })
    else:
        return JsonResponse({
            "status":"internal_error"
        })