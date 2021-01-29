from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from  dashboard.models import (
    ChapterEvent,
    ServiceEvent,
    PhilanthropyEvent,
    RecruitmentEvent,
    HealthAndSafetyEvent,
    Excuse
)
from dashboard.forms import ExcuseForm
from dashboard.utils import get_human_readable_model_name


def brother_chapter_event(request, event_id, view):
    """ Renders the brother page for chapter event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = ChapterEvent.objects.get(pk=event_id)
    form = ExcuseForm(request.POST or None)

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'form': form,
        'event': event,
        'excuse_exists': excuse.exists(),
        'brother': brother,
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists(),
        'button': 'Submit Excuse',
        'event_type': get_human_readable_model_name(event)
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "events/base-event.html", context)


def brother_service_event(request, event_id, view):
    """ Renders the brother page for service event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)
    event = ServiceEvent.objects.get(pk=event_id)
    rsvp_brother = event.rsvp_brothers.filter(id=brother.id)
    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if 'excuse' in request.POST:
            if form.is_valid():
                instance = form.save(commit=False)
                instance.brother = brother
                instance.event = event
                instance.save()
        if 'rsvp' in request.POST:
            event.rsvp_brothers.add(brother)
            event.save()
        if 'cancel_rsvp' in request.POST:
            event.rsvp_brothers.remove(brother)
            event.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'rsvpd': rsvp_brother.exists(),
        'event': event,
        'form': form,
        'excuse_exists': excuse.exists(),
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists(),
        'button': 'Submit Excuse',
        'event_type': get_human_readable_model_name(event)
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "events/service-event.html", context)


def brother_philanthropy_event(request, event_id, view):
    """ Renders the brother page for service event with a excuse form """
    if view is not 'general' and not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)
    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()
    rsvp_brother = event.rsvp_brothers.filter(id=brother.id)

    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if 'excuse' in request.POST:
            if form.is_valid():
                instance = form.save(commit=False)
                instance.brother = brother
                instance.event = event
                instance.save()
        if 'rsvp' in request.POST:
            if rsvp_brother.exists():
                event.rsvp_brothers.remove(brother)
            else:
                event.rsvp_brothers.add(brother)
            event.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'brothers_rsvp': brothers_rsvp,
        'rsvpd': rsvp_brother.exists(),
        'event': event,
        'form': form,
        'excuse_exists': excuse.exists(),
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists(),
        'button': 'Submit Excuse',
        'event_type': get_human_readable_model_name(event)
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "events/philanthropy-event.html", context)


def brother_recruitment_event(request, event_id, view):
    """ Renders the brother page for recruitment event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)

    event = RecruitmentEvent.objects.get(pk=event_id)
    attendees_pnms = event.attendees_pnms.all()

    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'form': form,
        'type': view,
        'attendees_pnms': attendees_pnms,
        'event': event,
        'excuse_exists': excuse.exists(),
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists(),
        'button': 'Submit Excuse',
        'event_type': get_human_readable_model_name(event)
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "events/recruitment-event.html", context)


def brother_hs_event(request, event_id, view):
    """ Renders the brother page for health and safety event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother Health and Safety events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)

    event = HealthAndSafetyEvent.objects.get(pk=event_id)

    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'event': event,
        'form': form,
        'excuse_exists': excuse.exists(),
        'brother': brother,
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists(),
        'button': 'Submit Excuse',
        'event_type': get_human_readable_model_name(event)
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "events/base-event.html", context)

