from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

import datetime

from dashboard.forms import (
    GPAForm,
)
from dashboard.models import (
    Brother,
    ScholarshipReport,
    Semester,
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
    """ Renders the Scholarship page listing all brother gpas """

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
        'brother_plans': brother_plans,
    })
    return render(request, "scholarship-chair/scholarship-chair.html", context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_plan(request, plan_id):
    """Renders Scholarship Plan page for the Scholarship Chair"""
    plan = ScholarshipReport.objects.get(pk=plan_id)

    context = {
        'type': 'scholarship-chair',
        'plan': plan,
    }

    return render(request, 'scholarship-chair/scholarship-report.html', context)


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

    return render(request, 'scholarship-chair/scholarship-gpa.html', context)


class ScholarshipReportEdit(DashboardUpdateView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ScholarshipReportEdit, self).get(request, *args, **kwargs)

    model = ScholarshipReport
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:scholarship_c')
    fields = ['cumulative_gpa', 'past_semester_gpa', 'scholarship_plan', 'active']
