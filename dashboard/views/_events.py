from django.http import HttpResponseRedirect
from django.shortcuts import render

from dashboard.forms import EventForm
from dashboard.models import Event, Brother, Position, EVENT_CHAIRS
from dashboard.utils import (
    save_event,
    verify_position,
    get_form_from_position,
)
from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(EVENT_CHAIRS + (Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER))
def event_add(request, position_slug):
    # since this view can be accessed from multiple different pages, in order to redirect back to those pages,
    # pass in a slug for the position doing a redirect on the slug should redirect back to the position's page

    form = get_form_from_position(position_slug, request)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
            save_event(instance, eligible_attendees)
            return HttpResponseRedirect('/' + position_slug)

    context = {
        'position': Position.objects.get(title=position_slug),
        'form': form,
    }
    return render(request, 'event-add.html', context)


class EventEdit(DashboardUpdateView):
    @verify_position(EVENT_CHAIRS + (Position.PositionChoices.VICE_PRESIDENT,
                                         Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER))
    def get(self, request, *args, **kwargs):
        return super(EventEdit, self).get(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        # each event has a slug field called 'slug' which contains the string for what url you should redirect to
        # Ex. 'philanthropy-chair' or 'vphs'
        return '/' + self.object.slug

    model = Event
    template_name = 'generic-forms/base-form.html'
    form_class = EventForm


class EventDelete(DashboardDeleteView):
    @verify_position(EVENT_CHAIRS + (Position.PositionChoices.VICE_PRESIDENT,
                                         Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER))
    def get(self, request, *args, **kwargs):
        return super(EventDelete, self).get(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        # each event has a slug field called 'slug' which contains the string for what url you should redirect to
        # Ex. 'philanthropy-chair' or 'vphs'
        return '/' + self.object.slug

    model = Event
    template_name = 'generic-forms/base-confirm-delete.html'