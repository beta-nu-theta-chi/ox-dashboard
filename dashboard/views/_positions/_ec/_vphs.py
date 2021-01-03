from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView, DeleteView

from dashboard.forms import HealthAndSafetyEventForm, EditBrotherAttendanceForm
from dashboard.models import Brother, HealthAndSafetyEvent, Event
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_semester,
    mark_attendance_list,
    save_event,
    update_eligible_brothers
)

@verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
def vphs(request):
    """ Renders the VPHS and the events they can create """
    events = HealthAndSafetyEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")
    committee_meetings, context = committee_meeting_panel('Vice President of Health and Safety')

    context.update({
        'position': 'Vice President of Health and Safety',
        'events': events,
    })
    return render(request, 'vphs.html', context)


@verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
def health_and_safety_event_add(request):
    """ Renders the VPHS adding an event """
    form = HealthAndSafetyEventForm(request.POST or None, initial={'name': 'Sacred Purpose Event'})

    if form.is_valid():
        # TODO: add google calendar event adding
        instance = form.save(commit=False)
        eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
        save_event(instance, eligible_attendees)
        return HttpResponseRedirect(reverse('dashboard:vphs'))

    context = {
        'title': 'Add New Health and Safety Event',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class HealthAndSafetyEdit(UpdateView):
    @verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
    def get(self, request, *args, **kwargs):
        return super(HealthAndSafetyEdit, self).get(request, *args, **kwargs)

    model = HealthAndSafetyEvent
    success_url = reverse_lazy('dashboard:vphs')
    form_class = HealthAndSafetyEventForm


class HealthAndSafetyDelete(DeleteView):
    @verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
    def get(self, request, *args, **kwargs):
        return super(HealthAndSafetyDelete, self).get(request, *args, **kwargs)

    model = HealthAndSafetyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:vphs')


def health_and_safety_event(request, event_id):
    """ Renders the vphs way of view events """
    event = Event.objects.get(pk=event_id)
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
    }
    return render(request, "hs-event.html", context)
