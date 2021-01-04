from dashboard.models import RecruitmentEvent, Photo
from dashboard.utils import photo_context, get_semester

from django.shortcuts import render

import datetime

def home(request):
    """ Renders home page """

    context = photo_context(Photo)
    recruitment_events = RecruitmentEvent.objects \
                                         .filter(semester=get_semester()) \
                                         .filter(date__gte=datetime.date.today()) \
                                         .order_by("date")
    context.update({
        'recruitment_events': recruitment_events,
    })

    return render(request, 'home.html', context)
