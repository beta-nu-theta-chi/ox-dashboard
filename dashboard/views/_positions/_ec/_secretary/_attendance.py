from django.shortcuts import render

import datetime

from dashboard.models import Brother, RecruitmentEvent, Event, Excuse
from dashboard.utils import verify_position, get_semester


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_attendance(request):
    """ Renders the secretary view for chapter attendance """
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name', 'first_name')
    events = Event.objects.filter(semester=get_semester(), mandatory=True, date__lt=datetime.date.today())\
        .exclude(pk__in=RecruitmentEvent.objects.all().values_list('pk', flat=True))
    accepted_excuses = Excuse.objects.filter(event__semester=get_semester(), status='1', event__in=events)
    brother_attendance = []

    # For each brother, appends a tuple to brother_attendance that contains the number of events excused, unexcused,
    # attended/excuse and events eligible for them to attend. The latter 2 are used to display the
    # attendance fraction
    for brother in brothers:
        events_eligible_list = events.filter(eligible_attendees=brother)
        events_eligible = events_eligible_list.count()
        events_attended = 0
        events_excused = 0
        events_unexcused = 0
        for event in events_eligible_list:
            if event.attendees_brothers.filter(id=brother.id).exists():
                events_attended += 1
            elif accepted_excuses.filter(brother=brother, event=event).exists():
                events_excused += 1
            else:
                events_unexcused += 1
        brother_attendance.append((brother, events_excused, events_unexcused, events_attended+events_excused, events_eligible))

    context = {
        'brother_attendance': brother_attendance,
        'position': 'Secretary'
    }

    return render(request, 'attendance.html', context)
