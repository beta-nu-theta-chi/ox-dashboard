from django.shortcuts import render, redirect

from dashboard.forms import (
    EditBrotherAttendanceForm,
)
from dashboard.models import (
    PhilanthropyEvent, Position,
)
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_semester,
    mark_attendance_list,
    update_eligible_brothers,
    verify_position,
    get_human_readable_model_name,
)


@verify_position([Position.PositionChoices.PHILANTHROPY_CHAIR, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    events = PhilanthropyEvent.objects.filter(semester=get_semester())
    committee_meetings, context = committee_meeting_panel(Position.PositionChoices.PHILANTHROPY_CHAIR)

    context.update({
        'events': events,
    })

    return render(request, 'philanthropy-chair.html', context)


@verify_position([Position.PositionChoices.PHILANTHROPY_CHAIR, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
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
                instance = form.clean()
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