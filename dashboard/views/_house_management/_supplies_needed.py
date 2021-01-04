from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dashboard.models import Supplies

def supplies_list(request):
    supplies = Supplies.objects.filter(done=False)
    supplies = [(e.what, e.when) for e in supplies]

    context = {'supplies': supplies}

    return render(request, 'list-supplies.html', context)
