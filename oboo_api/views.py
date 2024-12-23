from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse

from .models import Building


def index(request):
    return HttpResponse("Hello, world. You're at the Oboo API index.")

def buildings(request):
    buildings = Building.objects.all()
    buildings_dicts = [model_to_dict(building, fields=('id', 'name')) for building in buildings]
    return JsonResponse(buildings_dicts, safe=False)
