from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView

from dashboard.forms import ChapterEventForm, EditBrotherAttendanceForm
from dashboard.models import ChapterEvent, Event, Semester
from dashboard.utils import (
    attendance_list,
    forms_is_valid,
    mark_attendance_list,
    save_event,
    update_eligible_brothers,
    verify_position,
)

@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event(request, event_id):
    """ Renders the attendance sheet for any event """
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
    return render(request, "chapter-event.html", context)


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
    return render(request, "chapter-event.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event_add(request):
    """ Renders the Secretary way of adding ChapterEvents """
    form = ChapterEventForm(request.POST or None, initial={'name': 'Chapter Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            save_event(instance)
            return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'position': 'Secretary',
        'form': form,
    }
    return render(request, "event-add.html", context)


class ChapterEventEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ChapterEventEdit, self).get(request, *args, **kwargs)

    model = ChapterEvent
    success_url = reverse_lazy('dashboard:secretary')
    form_class = ChapterEventForm


class ChapterEventDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ChapterEventDelete, self).get(request, *args, **kwargs)

    model = ChapterEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_events(request):
    """ Renders a secretary view with all the ChapterEvent models ordered by date grouped by semester """
    events_by_semester = []
    semesters = Semester.objects.order_by("season").order_by("year").all()
    for semester in semesters:
        events = ChapterEvent.objects.filter(semester=semester).order_by("date")
        if len(events) == 0:
            events_by_semester.append([])
        else:
            events_by_semester.append(events)
    zip_list = zip(events_by_semester, semesters)
    context = {
        'list': zip_list,
        'position': "Secretary"
    }
    return render(request, "chapter-event-all.html", context)
