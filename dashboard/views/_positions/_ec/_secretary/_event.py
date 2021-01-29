from django.shortcuts import render, redirect

from dashboard.forms import EditBrotherAttendanceForm
from dashboard.models import ChapterEvent, Position
from dashboard.utils import (
    attendance_list,
    forms_is_valid,
    mark_attendance_list,
    update_eligible_brothers,
    verify_position,
    get_human_readable_model_name,
)


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def secretary_event(request, event_id):
    """ Renders the attendance sheet for any event """
    event = ChapterEvent.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.clean()
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


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def secretary_event_view(request, event_id):
    """ Renders the Secretary way of viewing old events """
    event = ChapterEvent.objects.get(pk=event_id)
    attendees = event.attendees_brothers.all().order_by("last_name", "first_name")

    context = {
        'type': 'ec-view',
        'attendees': attendees,
        'event': event,
    }
    return render(request, "events/base-event.html", context)
