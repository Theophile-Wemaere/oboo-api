import secrets
from datetime import datetime, timedelta

from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import make_naive

from .authfunc import handle_otp
from .models import Building, Floor, Room, TimeSlot, OTP, APIKey


def index(request):
    return HttpResponse("You're at the Oboo API index.")

def buildings(request):
    api_key = request.GET.get('api_key')
    email = request.GET.get('email')
    if api_key is None or email is None:
        return JsonResponse({'status': 'missing_parameter'}, status=400)

    # Check if the API Key belongs to the user and that the key is still valid
    stored_api_keys = APIKey.objects.filter(email=email).filter(key=api_key)
    for stored_api_key in stored_api_keys:
        now = datetime.now()
        if now < make_naive(stored_api_key.expiration) and stored_api_key.email == email:
            buildings = Building.objects.all()
            buildings_dicts = [model_to_dict(building, fields=('id', 'name', 'long_name', 'city')) for building in buildings]
            return JsonResponse(buildings_dicts, safe=False)

    return JsonResponse({'status': 'invalid_api_key'}, status=403)

def floors(request):
    api_key = request.GET.get('api_key')
    email = request.GET.get('email')
    if api_key is None or email is None:
        return JsonResponse({'status': 'missing_parameter'}, status=400)

    # Check if the API Key belongs to the user and that the key is still valid
    stored_api_keys = APIKey.objects.filter(email=email).filter(key=api_key)
    for stored_api_key in stored_api_keys:
        now = datetime.now()
        if now < make_naive(stored_api_key.expiration) and stored_api_key.email == email:
            floors = Floor.objects.all()
            floors_dicts = [model_to_dict(floor, fields=('id', 'number', 'name', 'building')) for floor in floors]
            return JsonResponse(floors_dicts, safe=False)

    return JsonResponse({'status': 'invalid_api_key'}, status=403)

def rooms(request):
    api_key = request.GET.get('api_key')
    email = request.GET.get('email')
    if api_key is None or email is None:
        return JsonResponse({'status': 'missing_parameter'}, status=400)

    # Check if the API Key belongs to the user and that the key is still valid
    stored_api_keys = APIKey.objects.filter(email=email).filter(key=api_key)
    for stored_api_key in stored_api_keys:
        now = datetime.now()
        if now < make_naive(stored_api_key.expiration) and stored_api_key.email == email:
            rooms = Room.objects.all()
            rooms_dicts = [model_to_dict(room, fields=('id', 'number', 'name', 'floor')) for room in rooms]
            return JsonResponse(rooms_dicts, safe=False)

    return JsonResponse({'status': 'invalid_api_key'}, status=403)
def time_slots(request):
    api_key = request.GET.get('api_key')
    email = request.GET.get('email')
    if api_key is None or email is None:
        return JsonResponse({'status': 'missing_parameter'}, status=400)

    # Check if the API Key belongs to the user and that the key is still valid
    stored_api_keys = APIKey.objects.filter(email=email).filter(key=api_key)
    for stored_api_key in stored_api_keys:
        now = datetime.now()
        if now < make_naive(stored_api_key.expiration) and stored_api_key.email == email:
            time_slots = TimeSlot.objects.all()
            time_slots_dicts = [model_to_dict(time_slot, fields=('id', 'subject', 'start_time', 'end_time', 'room')) for time_slot in time_slots]
            return JsonResponse(time_slots_dicts, safe=False)

    return JsonResponse({'status': 'invalid_api_key'}, status=403)
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
            "status":"invalid_domain"
        })
    elif status == -2:
        return JsonResponse({
            "status":"bad_emails"
        })
    else:
        return JsonResponse({
            "status":"internal_error"
        })

def generate_api_key(request):
    email = request.GET.get('email', None)
    otp = request.GET.get('otp', None)

    if otp is None or email is None:
        return JsonResponse({
            "status":"missing_parameter",
            "key":""
        })

    # Get all OTP objects that have a corresponding code and email
    stored_otps = OTP.objects.filter(email=email).filter(code=otp)
    # Then, ensure the code is still valid
    for stored_otp in stored_otps:
        now = datetime.now()
        if now < (make_naive(stored_otp.expiration)):
            api_key = secrets.token_urlsafe(64)[:64]
            now = datetime.now()
            APIKey.objects.create(key=api_key, email=email, created_at=now, expiration=now + timedelta(days=30))
            return JsonResponse({
                "status": "success",
                "key":f"{api_key}"
            })
        else:
            print(f"[OTP Validation] Code {otp} for email {email} is valid but expired: {now} < {(make_naive(stored_otp.expiration))} ")
    return JsonResponse({
        "status": "invalid_code",
        "key": ""
    })
