from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

import datetime

from dashboard.models import MeetABrother, Brother, OnlineMedia


def meet_a_brother(request):
    start_date = datetime.datetime(2000, 1, 1)
    candidates = Brother.objects.filter(brother_status=0)

    weeks = MeetABrother.objects.filter(week__range=(start_date, datetime.datetime.now())).order_by('-week').values_list('week', flat=True).distinct
    try:
        discord = OnlineMedia.objects.get(name='Discord')
    except ObjectDoesNotExist:
        discord = None

    context = {
        'candidates': candidates,
        'weeks': weeks,
        'discord': discord,
    }

    return render(request, 'general/meet-a-brother.html', context)
