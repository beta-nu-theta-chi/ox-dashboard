from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from dashboard.forms import ChapterEventForm, EventForm, EditBrotherAttendanceForm
from dashboard.models import ChapterEvent, Event, Semester, Brother
from dashboard.utils import (
    attendance_list,
    forms_is_valid,
    mark_attendance_list,
    save_event,
    update_eligible_brothers,
    verify_position,
    get_human_readable_model_name,
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
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


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
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


@verify_position(['Philanthropy Chair', 'Service Chair', 'Secretary', 'Vice President of Health and Safety', 'President', 'Adviser'])
def event_add(request, position_slug):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    position = Position.PositionChoices(position_slug).label
    form = get_form_from_position(position, request)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
            save_event(instance, eligible_attendees)
            return HttpResponseRedirect('/' + position_slug)

    context = {
        'position': position,
        'form': form,
    }
    return render(request, 'event-add.html', context)


class EventEdit(DashboardUpdateView):
    @verify_position(['Philanthropy Chair', 'Service Chair', 'Secretary', 'Vice President of Health and Safety', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(EventEdit, self).get(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return '/' + self.object.slug

    model = Event
    template_name = 'generic-forms/base-form.html'
    form_class = EventForm


class EventDelete(DashboardDeleteView):
    @verify_position(['Philanthropy Chair', 'Service Chair', 'Secretary', 'Vice President of Health and Safety', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(EventDelete, self).get(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return '/' + self.object.slug

    model = Event
    template_name = 'generic-forms/base-confirm-delete.html'
