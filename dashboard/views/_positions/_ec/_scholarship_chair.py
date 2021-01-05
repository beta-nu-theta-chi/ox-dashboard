from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

import datetime

from dashboard.forms import (
    GPAForm,
    StudyTableEventForm,
)
from dashboard.models import (
    Brother,
    ScholarshipReport,
    Semester,
    StudyTableEvent,
)
from dashboard.utils import (
    attendance_list,
    committee_meeting_panel,
    forms_is_valid,
    get_season_from,
    get_semester,
    verify_position,
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c(request):
    """ Renders the Scholarship page listing all brother gpas and study table attendance """
    events = StudyTableEvent.objects.filter(semester=get_semester()).order_by("date")

    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")
    plans = []

    for brother in brothers:
        plan = ScholarshipReport.objects.filter(semester=get_semester(), brother__id=brother.id)
        if plan.exists():
            plan = plan[0]
        else:
            plan = ScholarshipReport(brother=brother, semester=get_semester())
            plan.save()
        plans.append(plan)

    brother_plans = zip(brothers, plans)

    committee_meetings, context = committee_meeting_panel('Scholarship Chair')

    context.update({
        'position': 'Scholarship Chair',
        'events': events,
        'brother_plans': brother_plans,
    })
    return render(request, "scholarship-chair.html", context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def study_table_event(request, event_id):
    """ Renders the scholarship chair way of view StudyTables """
    event = StudyTableEvent.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    if request.method == 'POST':
        if forms_is_valid(brother_form_list):
            for counter, form in enumerate(brother_form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_brothers.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_brothers.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
    }
    return render(request, "studytable-event.html", context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_event_add(request):
    """ Renders the scholarship chair way of adding StudyTableEvents """
    form = StudyTableEventForm(request.POST or None, initial={'name': 'Scholarship Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
            save_event(instance, eligible_attendees)
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'position': 'Scholarship Chair',
        'form': form,
    }
    return render(request, "event-add.html", context)


class StudyEventDelete(DashboardDeleteView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(StudyEventDelete, self).get(request, *args, **kwargs)

    model = StudyTableEvent
    template_name = 'generic_forms/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:scholarship_c')


class StudyEventEdit(DashboardUpdateView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(StudyEventEdit, self).get(request, *args, **kwargs)

    model = StudyTableEvent
    template_name = 'generic_forms/studytableevent_form.html'
    success_url = reverse_lazy('dashboard:scholarship_c')
    form_class = StudyTableEventForm


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_plan(request, plan_id):
    """Renders Scholarship Plan page for the Scholarship Chair"""
    plan = ScholarshipReport.objects.get(pk=plan_id)
    events = StudyTableEvent.objects.filter(semester=get_semester()).exclude(date__gt=datetime.date.today())
    study_tables_attended = 0
    study_tables_count = len(events)

    for event in events:
        if event.attendees_brothers.filter(id=plan.brother.id).exists():
            study_tables_attended += 1

    context = {
        'type': 'scholarship-chair',
        'plan': plan,
        'study_tables_count': study_tables_count,
        'study_tables_attended': study_tables_attended,
    }

    return render(request, 'scholarship-report.html', context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_gpa(request):
    """Renders Scholarship Gpa update page for the Scholarship Chair"""
    plans = ScholarshipReport.objects.filter(semester=get_semester()).order_by("brother__last_name")
    form_list = []

    for plan in plans:
        new_form = GPAForm(request.POST or None, initial={'cum_GPA': plan.cumulative_gpa,
                                                          'past_GPA': plan.past_semester_gpa}, prefix=plan.id)
        form_list.append(new_form)

    form_plans = zip(form_list, plans)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                plan = plans[counter]
                plan.cumulative_gpa = instance['cum_GPA']
                plan.past_semester_gpa = instance['past_GPA']
                plan.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'form_plans': form_plans,
    }

    return render(request, 'scholarship-gpa.html', context)


class ScholarshipReportEdit(DashboardUpdateView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ScholarshipReportEdit, self).get(request, *args, **kwargs)

    model = ScholarshipReport
    template_name = 'generic_forms/base_form.html'
    success_url = reverse_lazy('dashboard:scholarship_c')
    fields = ['cumulative_gpa', 'past_semester_gpa', 'scholarship_plan', 'active']
