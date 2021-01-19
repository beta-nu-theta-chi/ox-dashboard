from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect

from dashboard.forms import HealthAndSafetyEventForm, EditBrotherAttendanceForm
from dashboard.models import Brother, HealthAndSafetyEvent, Event
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_semester,
    mark_attendance_list,
    save_event,
    update_eligible_brothers,
    verify_position,
    get_human_readable_model_name
)


@verify_position([ 'vphs', 'vice-president', 'president', 'adviser'])
def vphs(request):
    """ Renders the VPHS and the events they can create """
    events = HealthAndSafetyEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")
    committee_meetings, context = committee_meeting_panel('vphs')

    context.update({
        'events': events,
    })
    return render(request, 'vphs.html', context)


def health_and_safety_event(request, event_id):
    """ Renders the vphs way of view events """
    event = HealthAndSafetyEvent.objects.get(pk=event_id)
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
        'event': event,
        'form': form,
        'event_type': get_human_readable_model_name(event),
    }
    return render(request, "events/base-event.html", context)
