from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy

from dashboard.forms import (
    EditBrotherAttendanceForm,
    Semester,
    ServiceEventForm,
    ServiceSubmissionResponseForm,
)
from dashboard.models import (
    Brother,
    Event,
    ServiceEvent,
    ServiceSubmission,
)
from dashboard.utils import (
    attendance_list,
    get_season_from,
    get_semester,
    mark_attendance_list,
    update_eligible_brothers,
    verify_position,
    save_event,
    get_human_readable_model_name,
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['Service Chair', 'Adviser'])
def service_c(request):
    """ Renders the service chair page with service submissions """
    events = ServiceEvent.objects.filter(semester=get_semester())
    submissions_pending = ServiceSubmission.objects.filter(semester=get_semester(), status='0').order_by("date")

    submissions_submitted = ServiceSubmission.objects.filter(semester=get_semester(), status='1').order_by(
        "date")

    hours_pending = 0
    for submission in submissions_pending:
        hours_pending += submission.hours
    for submission in submissions_submitted:
        hours_pending += submission.hours

    hours_approved = 0
    submissions_approved = ServiceSubmission.objects.filter(semester=get_semester(), status='2')
    for submission in submissions_approved:
        hours_approved += submission.hours

    context = {
        'events': events,
        'hours_approved': hours_approved,
        'hours_pending': hours_pending,
        'submissions_pending': submissions_pending,
        'submissions_submitted': submissions_submitted,
    }
    return render(request, 'service-chair.html', context)


@verify_position(['Service Chair', 'Adviser'])
def service_c_event(request, event_id):
    """ Renders the service chair way of adding ServiceEvent """
    event = ServiceEvent.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
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

    return render(request, 'events/service-event.html', context)


class ServiceEventDelete(DashboardDeleteView):
    @verify_position(['Service Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ServiceEventDelete, self).get(request, *args, **kwargs)

    model = ServiceEvent
    template_name = 'generic_forms/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:service_c')


class ServiceEventEdit(DashboardUpdateView):
    @verify_position(['Service Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ServiceEventEdit, self).get(request, *args, **kwargs)

    model = ServiceEvent
    template_name = 'generic_forms/base_form.html'
    success_url = reverse_lazy('dashboard:service_c')
    form_class = ServiceEventForm


@verify_position(['Service Chair', 'Adviser'])
def service_c_submission_response(request, submission_id):
    """ Renders the service chair way of responding to submissions """
    submission = ServiceSubmission.objects.get(pk=submission_id)
    form = ServiceSubmissionResponseForm(request.POST or None, initial={'status': submission.status})

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            submission.status = instance['status']
            submission.save()
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'submission': submission,
        'type': 'response',
        'form': form,
    }

    return render(request, 'service-submission.html', context)


@verify_position(['Service Chair', 'Adviser'])
def service_c_event_add(request):
    """ Renders the service chair way of adding ServiceEvent """
    form = ServiceEventForm(request.POST or None, initial={'name': 'Service Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
            save_event(instance, eligible_attendees)
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'position': 'Service Chair',
        'form': form,
    }

    return render(request, 'event-add.html', context)


@verify_position(['Service Chair', 'Adviser'])
def service_c_hours(request):
    """ Renders the service chair way of viewing total service hours by brothers """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")
    approved_submissions = ServiceSubmission.objects.filter(status='2')
    pending_submissions = ServiceSubmission.objects.exclude(status='2').exclude(status='3')

    approved_hours_list = []
    pending_hours_list = []

    for brother in brothers:
        approved_hours = 0
        pending_hours = 0
        for submission in approved_submissions:
            if submission.brother == brother:
                approved_hours += submission.hours
        for submission in pending_submissions:
            if submission.brother == brother:
                pending_hours += submission.hours
        approved_hours_list.append(approved_hours)
        pending_hours_list.append(pending_hours)

    brother_hours_list = zip(brothers, approved_hours_list, pending_hours_list)

    context = {
        'position': 'Service Chair',
        'brother_hours_list': brother_hours_list,
    }

    return render(request, "service-hours-list.html", context)
