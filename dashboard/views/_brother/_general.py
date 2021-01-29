import datetime

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from dashboard.models import (
    ChapterEvent,
    ServiceEvent,
    PhilanthropyEvent,
    RecruitmentEvent,
    HealthAndSafetyEvent,
    Excuse,
    PotentialNewMember,
    ServiceSubmission,
    OnlineMedia,
    Brother
)
from dashboard.forms import BrotherEditForm
from dashboard.utils import (
    create_attendance_list,
    get_season,
    get_semester,
    get_year,
    notified_by,
    notifies,
    verify_brother
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView


def brother_view(request):
    """ Renders the brother page of current user showing all standard brother information """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother needs to be logged in before viewing brother portal")
        return HttpResponseRedirect(reverse('dashboard:home'))
    brother = request.user.brother
    semester = get_semester()
    hs_events = HealthAndSafetyEvent.objects.filter(semester=semester, eligible_attendees=brother).order_by("date")
    chapter_events = ChapterEvent.objects.filter(semester=semester, eligible_attendees=brother).order_by("date")

    # creates lists of events that were pending and approved for the current brother
    excuses = Excuse.objects.filter(brother=brother, event__semester=semester).order_by("event__date")
    excuses_pending = excuses.filter(status='0').values_list('event', flat=True)
    excuses_approved = excuses.filter(status='1').values_list('event', flat=True)

    operational_committees = []
    standing_committees = []
    meetings = []

    for committee in brother.committee_set.all():
        if committee.in_standing():
            standing_committees.append(committee)
        elif committee.in_operational():
            operational_committees.append(committee)
        for meeting in committee.meetings.all():
            meetings.append(meeting)

    # creates a list of tuples: (event, attendance type)
    chapter_attendance = create_attendance_list(chapter_events, excuses_pending, excuses_approved, brother)

    hs_attendance = create_attendance_list(hs_events, excuses_pending, excuses_approved, brother)

    current_season = get_season()
    recruitment_events = RecruitmentEvent.objects.filter(semester__season=current_season, semester__year=get_year(),
                                                                eligible_attendees=brother).order_by("date")
    recruitment_events_next = RecruitmentEvent.objects.filter(semester__year=get_year(), eligible_attendees=brother)\
        .exclude(semester__season=current_season).order_by("date")
    recruitment_attendance = create_attendance_list(recruitment_events, excuses_pending, excuses_approved, brother)

    pnms = PotentialNewMember.objects.filter(Q(primary_contact=brother) |
                                             Q(secondary_contact=brother) |
                                             Q(tertiary_contact=brother)).order_by("last_name", "first_name")

    service_events = ServiceEvent.objects.filter(semester=semester, eligible_attendees=brother).order_by("date")
    service_attendance = create_attendance_list(service_events, excuses_pending, excuses_approved, brother)

    # Service submissions
    submissions_pending = ServiceSubmission.objects.filter(brother=brother, semester=semester,
                                                           status='0').order_by("date")
    submissions_submitted = ServiceSubmission.objects.filter(brother=brother, semester=semester,
                                                             status='1').order_by("date")
    submissions_approved = ServiceSubmission.objects.filter(brother=brother, semester=semester,
                                                            status='2').order_by("date")
    submissions_denied = ServiceSubmission.objects.filter(brother=brother, semester=semester,
                                                          status='3').order_by("date")
    hours_pending = 0
    for submission in submissions_pending:
        hours_pending += submission.hours
    for submission in submissions_submitted:
        hours_pending += submission.hours

    hours_approved = 0
    for submission in submissions_approved:
        hours_approved += submission.hours

    philanthropy_events = PhilanthropyEvent.objects.filter(semester=semester, eligible_attendees=brother) \
        .order_by("start_time").order_by("date")

    philanthropy_attendance = create_attendance_list(philanthropy_events, excuses_pending, excuses_approved, brother)

    mab = None

    if brother.brother_status == '0':
        mab = [x.brother for x in brother.candidate_mab.filter(completed=False)]
    elif brother.brother_status == '1':
        mab = [x.candidate for x in brother.brother_mab.filter(completed=False)]

    try:
        discord = OnlineMedia.objects.get(name='Discord')
    except ObjectDoesNotExist:
        discord = None

    if request.method == 'POST':
        pk = request.POST.get('id')
        if brother.brother_status == '0':
            mabro = brother.candidate_mab.get(brother=pk)
            mabro.completed = True
            mabro.save()
        elif brother.brother_status == '1':
            mabro = brother.brother_mab.get(candidate=pk)
            mabro.completed = True
            mabro.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'brother': brother,
        'chapter_attendance': chapter_attendance,
        'operational_committees': operational_committees,
        'standing_committees': standing_committees,
        'meetings': meetings,
        'hs_attendance': hs_attendance,
        'recruitment_events_next': recruitment_events_next,
        'recruitment_attendance': recruitment_attendance,
        'pnms': pnms,
        'service_attendance': service_attendance,
        'submissions_pending': submissions_pending,
        'submissions_submitted': submissions_submitted,
        'submissions_approved': submissions_approved,
        'submissions_denied': submissions_denied,
        'philanthropy_attendance': philanthropy_attendance,
        'hours_approved': hours_approved,
        'hours_pending': hours_pending,
        'type': 'brother-view',
        'notifies': notifies(brother),
        'notified_by': notified_by(brother),
        'mab': mab,
        'discord': discord,
    }
    return render(request, "brother.html", context)


class BrotherEdit(DashboardUpdateView):
    def get(self, request, *args, **kwargs):
        brother = Brother.objects.get(pk=self.kwargs['pk'])
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(BrotherEdit, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:brother')
    form_class = BrotherEditForm
