from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from dashboard.forms import (
    EditBrotherAttendanceForm,
    EventForm,
)
from dashboard.models import (
    Brother,
    PhilanthropyEvent,
    Semester,
    Position,
)
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_season_from,
    get_semester,
    mark_attendance_list,
    update_eligible_brothers,
    verify_position,
    save_event,
    get_human_readable_model_name,
    get_form_from_position,
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    events = PhilanthropyEvent.objects.filter(semester=get_semester())
    committee_meetings, context = committee_meeting_panel('Philanthropy Chair')

    context.update({
        'position': 'Philanthropy Chair',
        'position_slug': 'philanthropy-chair',
        'events': events,
    })

    return render(request, 'philanthropy-chair.html', context)


@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c_event(request, event_id):
    """ Renders the philanthropy event view """
    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'brothers_rsvp': brothers_rsvp,
        'event': event,
        'form': form,
        'event_type': get_human_readable_model_name(event),
    }

    return render(request, 'events/philanthropy-event.html', context)


#@verify_position(['Philanthropy Chair', 'Adviser'])
def event_add(request, position_slug):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    position = Position.PositionChoices(position_slug).label
    form = get_form_from_position(position, request)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
            slug = save_event(instance, eligible_attendees)
            return HttpResponseRedirect('/' + position_slug)

    context = {
        'position': position,
        'form': form,
    }
    return render(request, 'event-add.html', context)