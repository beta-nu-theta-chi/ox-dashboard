from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect

import datetime

from dashboard.forms import (
    BrotherAttendanceForm,
    EventForm,
    EditBrotherAttendanceForm,
    CommitteeMeetingForm,
)
from dashboard.models import (
    Committee,
    CommitteeMeetingEvent,
    Position, Event, committee_chairs,
)
from dashboard.utils import (
    create_recurring_meetings,
    forms_is_valid,
    mark_attendance_list,
    save_event,
    update_eligible_brothers,
    verify_position,
)

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


class CommitteeDelete(DashboardDeleteView):
    @verify_position([Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
    def get(self, request, *args, **kwargs):
        return super(CommitteeDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashboard:committee_list')

    model = Committee
    template_name = 'generic-forms/base-confirm-delete.html'


class CommitteeEdit(DashboardUpdateView):
    def get(self, request, *args, **kwargs):
        return super(CommitteeEdit, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return '/' + self.object.chair.title

    def form_valid(self, form):
        self.object.meetings.filter(recurring=True).exclude(date__lt=datetime.date.today()+datetime.timedelta(days=1)).delete()
        committee = self.object.committee
        form.save()
        instance = form.clean()
        create_recurring_meetings(instance, committee)
        return super().form_valid(form)

    model = Committee
    template_name = 'generic-forms/committee-form.html'
    fields = ['meeting_day', 'meeting_time', 'meeting_interval']


def committee_event(request, event_id):
    event = CommitteeMeetingEvent.objects.get(pk=event_id)

    brothers = event.eligible_attendees.all()
    brother_form_list = []
    current_brother = request.user.brother

    if current_brother in event.committee.chair.brothers.all():
        view_type = 'chairman'
    else:
        view_type = 'brother'

    for counter, brother in enumerate(brothers):
        new_form = BrotherAttendanceForm(request.POST or None, initial={'present':  event.attendees_brothers.filter(id=brother.id).exists()},
                                         prefix=counter,
                                         brother="- %s %s" % (brother.first_name, brother.last_name))
        brother_form_list.append(new_form)

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
        'type': view_type,
        'brother_form_list': brother_form_list,
        'event': event,
        'form': form,
    }

    return render(request, "committee-event.html", context)


@verify_position(committee_chairs+ (Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER))
def committee_event_add(request, position_slug):
    """ Renders the committee meeting add page """
    form = CommitteeMeetingForm(request.POST or None)
    position = Position.objects.get(title=position_slug)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            committee = position.committee
            eligible_attendees = committee.members.order_by('last_name')
            instance.committee = committee
            instance.name = committee.get_committee_display() + " Committee Meeting"
            instance.slug = committee.chair.title
            save_event(instance, eligible_attendees)
            return HttpResponseRedirect('/' + instance.slug)

    context = {
        'title': 'Committee Meeting',
        'form': form,
        'position': position,
    }
    return render(request, 'event-add.html', context)


class CommitteeEventEdit(DashboardUpdateView):
    @verify_position(committee_chairs + (Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER))
    def get(self, request, *args, **kwargs):
        return super(CommitteeEventEdit, self).get(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        # each event has a slug field called 'slug' which contains the string for what url you should redirect to
        # Ex. 'philanthropy-chair' or 'vphs'
        return '/' + self.object.slug

    model = Event
    template_name = 'generic-forms/committee-meeting-form.html'
    form_class = EventForm
