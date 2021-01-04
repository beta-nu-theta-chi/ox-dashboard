from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from dashboard.forms import BrotherMassEntryForm
from dashboard.views._positions._ec._secretary._mass_entry import (
    create_mass_entry_brothers,
    staged_mass_entry_brothers,
)

from dashboard.models import ChapterEvent, Excuse, RecruitmentEvent
from dashboard.utils import get_semester, verify_position

@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by("date_submitted", "event__date")
    events = ChapterEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")

    brothers = []

    if request.method == 'POST':
        mass_entry_form = BrotherMassEntryForm(request.POST)
        mass_entry_form.fields['brothers'].widget.attrs['readonly'] = False
        is_entry = False

        if "confirmation" in request.POST:
            create_mass_entry_brothers(request, mass_entry_form)
            return HttpResponseRedirect(reverse('dashboard:home'))

        elif "goback" in request.POST:
            is_entry = True  # just want to go back to adding/editting data

        # however else we got here, we need to show the staged data
        else:
            brothers = staged_mass_entry_brothers(mass_entry_form)
    else:
        mass_entry_form = BrotherMassEntryForm()
        is_entry = True

    context = {
        'excuses': excuses,
        'events': events,
        'mass_entry_form': mass_entry_form,
        'is_entry': is_entry, # TODO change to have post stuff
        'brothers': brothers,
    }
    return render(request, 'secretary.html', context)
