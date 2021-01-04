from django.shortcuts import render

from dashboard.models import MinecraftPhoto
from dashboard.utils import photo_context

def minecraft(request):
    return render(request, 'minecraft.html', photo_context(MinecraftPhoto))
