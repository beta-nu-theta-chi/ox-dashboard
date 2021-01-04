from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView

from dashboard.forms import (
    EditBrotherAttendanceForm,
    PhilanthropyEventForm,
)
from dashboard.models import (
    Brother,
    PhilanthropyEvent,
    Semester,
)
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_season_from,
    get_semester,
    mark_attendance_list,
    update_eligible_brothers,
    verify_position
)

@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    events = PhilanthropyEvent.objects.filter(semester=get_semester())
    committee_meetings, context = committee_meeting_panel('Philanthropy Chair')

    context.update({
        'position': 'Philanthropy Chair',
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
    }

    return render(request, 'philanthropy-event.html', context)


@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c_event_add(request):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    form = PhilanthropyEventForm(request.POST or None, initial={'name': 'Philanthropy Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            semester, _ = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
                   year=instance.date.year)
            instance.semester = semester
            instance.save()
            instance.eligible_attendees.set(Brother.objects.exclude(brother_status='2').order_by('last_name'))
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:philanthropy_c'))

    context = {
        'position': 'Philanthropy Chair',
        'form': form,
    }
    return render(request, 'event-add.html', context)


class PhilanthropyEventDelete(DeleteView):
    @verify_position(['Philanthropy Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PhilanthropyEventDelete, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:philanthropy_c')


class PhilanthropyEventEdit(UpdateView):
    @verify_position(['Philanthropy Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PhilanthropyEventEdit, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    success_url = reverse_lazy('dashboard:philanthropy_c')
    form_class = PhilanthropyEventForm
