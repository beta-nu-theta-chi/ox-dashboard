from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify

import csv
import datetime

from dashboard.forms import (
    EditBrotherAttendanceForm,
    PnmAttendanceForm,
    PotentialNewMemberForm,
    RecruitmentEventForm,
)
from dashboard.models import (
    Brother,
    Excuse,
    PotentialNewMember,
    RecruitmentEvent,
    Semester
)
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_season_from,
    get_season,
    get_semester,
    get_year,
    mark_attendance_list,
    update_eligible_brothers,
    verify_position,
    get_human_readable_model_name,
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c(request):
    """ Renders Recruitment chair page with events for the current and following semester """
    events = RecruitmentEvent.objects.all()
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0',
        event__in=events).order_by("date_submitted", "event__date")
    current_season = get_season()
    if current_season == '0':
        semester_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year())
    else:
        semester_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year())

    potential_new_members = PotentialNewMember.objects.all()

    committee_meetings, context = committee_meeting_panel('Recruitment Chair')

    context.update({
        'position': 'Recruitment Chair',
        'events': semester_events,
        'events_future': semester_events_next,
        'potential_new_members': potential_new_members,
        'excuses': excuses,
    })
    return render(request, 'recruitment-chair.html', context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_all_excuses(request):
    """ Renders Excuse archive"""
    excuses = Excuse.objects.exclude(status='0').filter(event__in=RecruitmentEvent.objects.all()).order_by('brother__last_name', 'event__date')

    context = {
        'excuses': excuses,
        'position': 'Recruitment Chair',
    }
    return render(request, 'excuses-archive.html', context)


def all_pnm_csv(request):
    """Returns a list of pnms as a csv"""
    potential_new_members = PotentialNewMember.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_pnms.csv"'
    writer = csv.writer(response)
    fields = [f.name for f in PotentialNewMember._meta.get_fields()][1:]
    writer.writerow(fields)
    for pnm in potential_new_members:
        row = []
        for field in fields:
            row.append(getattr(pnm, field))
        writer.writerow(row)

    return response


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_rush_attendance(request):
    """ Renders Scholarship chair page with rush attendance """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")
    events = RecruitmentEvent.objects.filter(semester=get_semester(), rush=True) \
        .exclude(date__gt=datetime.date.today())
    events_attended_list = []

    for brother in brothers:
        events_attended = 0
        for event in events:
            if event.attendees_brothers.filter(id=brother.id).exists():
                events_attended += 1
        events_attended_list.append(events_attended)

    rush_attendance = zip(brothers, events_attended_list)

    context = {
        'rush_attendance': rush_attendance,
    }

    return render(request, 'recruitment-chair-rush-attendance.html', context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_pnm(request, pnm_id):
    """ Renders PNM view for recruitment chair """
    pnm = PotentialNewMember.objects.get(pk=pnm_id)
    events = RecruitmentEvent.objects.filter(semester=get_semester()).order_by("date").all()

    attended_events = []
    for event in events:
        if event.attendees_pnms.filter(id=pnm_id).exists():
            attended_events.append(event)

    context = {
        'type': 'recruitment-chair-view',
        'events': attended_events,
        'pnm': pnm,
    }
    return render(request, 'potential-new-member.html', context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_pnm_add(request):
    """ Renders the recruitment chair way of adding PNMs """
    form = PotentialNewMemberForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:recruitment_c'))

    context = {
        'title': 'Add Potential New Member',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class PnmDelete(DashboardDeleteView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PnmDelete, self).get(request, *args, **kwargs)

    model = PotentialNewMember
    template_name = 'generic_forms/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:recruitment_c')


class PnmEdit(DashboardUpdateView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PnmEdit, self).get(request, *args, **kwargs)

    model = PotentialNewMember
    template_name = 'generic_forms/base_form.html'
    success_url = reverse_lazy('dashboard:recruitment_c')
    form_class = PotentialNewMemberForm


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_event(request, event_id):
    """ Renders the recruitment chair way of view RecruitmentEvents """
    event = RecruitmentEvent.objects.get(pk=event_id)
    pnms = PotentialNewMember.objects.all().order_by('last_name')
    pnm_form_list = []
    brothers, brother_form_list = attendance_list(request, event)

    num_actives = len(brothers)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    for counter, pnm in enumerate(pnms):
        new_form = PnmAttendanceForm(request.POST or None, initial={'present': event.attendees_pnms.filter(pk=pnm.id).exists()},
                                     prefix=num_actives + counter,
                                     pnm="- %s %s" % (pnm.first_name, pnm.last_name))
        pnm_form_list.append(new_form)

    if request.method == 'POST':
        if "updatebrother" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "updatepnm" in request.POST:
            if forms_is_valid(pnm_form_list):
                mark_attendance_list(pnm_form_list, pnms, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'pnm_form_list': pnm_form_list,
        'brother_form_list': brother_form_list,
        'event': event,
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'form': form,
        'event_type': get_human_readable_model_name(event),
    }
    return render(request, "events/recruitment-event.html", context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_event_add(request):
    """ Renders the recruitment chair way of adding RecruitmentEvents """
    form = RecruitmentEventForm(request.POST or None, initial={'name': 'Recruitment Event'})
    if request.method == 'POST':
        form = RecruitmentEventForm(request.POST, request.FILES or None)
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
            save_event(instance, eligible_attendees)
            return HttpResponseRedirect(reverse('dashboard:recruitment_c'))

    context = {
        'position': 'Recruitment Chair',
        'form': form,
    }
    return render(request, "event-add.html", context)


class RecruitmentEventDelete(DashboardDeleteView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(RecruitmentEventDelete, self).get(request, *args, **kwargs)

    model = RecruitmentEvent
    template_name = 'generic_forms/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:recruitment_c')


class RecruitmentEventEdit(DashboardUpdateView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(RecruitmentEventEdit, self).get(request, *args, **kwargs)

    form_class = RecruitmentEventForm
    template_name = 'generic_forms/base_form.html'
    model = RecruitmentEvent
    success_url = reverse_lazy('dashboard:recruitment_c')
