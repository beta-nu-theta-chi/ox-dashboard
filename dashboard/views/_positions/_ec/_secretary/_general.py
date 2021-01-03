from django.shortcuts import render

from dashboard.views._positions._ec._secretary._mass_entry import brother_mass_entry_form

from dashboard.models import ChapterEvent, Excuse, RecruitmentEvent
from dashboard.utils import get_semester

@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by("date_submitted", "event__date")
    events = ChapterEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")

    mass_entry_form, is_entry, brothers = brother_mass_entry_form(request)

    context = {
        'excuses': excuses,
        'events': events,
        'mass_entry_form': mass_entry_form,
        'is_entry': is_entry, # TODO change to have post stuff
        'brothers': brothers,
    }
    return render(request, 'secretary.html', context)
