from django.shortcuts import render

import datetime

from dashboard.models import Brother, ChapterEvent, Excuse
from dashboard.utils import verify_position, get_semester

@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_attendance(request):
    """ Renders the secretary view for chapter attendance """
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    events = ChapterEvent.objects.filter(semester=get_semester(), mandatory=True)\
        .exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []

    for brother in brothers:
        events_excused = 0
        events_unexcused = 0
        for event in events:
            if not event.attendees_brothers.filter(id=brother.id).exists():
                if excuses.filter(brother=brother, event=event).exists():
                    events_excused += 1
                else:
                    events_unexcused += 1
        events_excused_list.append(events_excused)
        events_unexcused_list.append(events_unexcused)

    brother_attendance = zip(brothers, events_excused_list, events_unexcused_list)

    context = {
        'brother_attendance': brother_attendance,
    }

    return render(request, 'chapter-event-attendance.html', context)
