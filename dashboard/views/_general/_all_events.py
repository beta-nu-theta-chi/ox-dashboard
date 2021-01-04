from django.shortcuts import render

from dashboard.models import (
    ChapterEvent,
    RecruitmentEvent,
    ServiceEvent,
    PhilanthropyEvent,
    HealthAndSafetyEvent
)
from dashboard.utils import get_semester

def event_list(request):
    """Renders all the semester events"""
    chapter_events = ChapterEvent.objects.filter(semester=get_semester()).order_by("date")
    recruitment_events = RecruitmentEvent.objects.filter(semester=get_semester()).order_by("date")
    service_events = ServiceEvent.objects.filter(semester=get_semester()).order_by("date")
    philanthropy_events = PhilanthropyEvent.objects.filter(semester=get_semester()).order_by("date")
    hs_events = HealthAndSafetyEvent.objects.filter(semester=get_semester()).order_by("date")

    context = {
        'chapter_events': chapter_events,
        'recruitment_events': recruitment_events,
        'service_events': service_events,
        'philanthropy_events': philanthropy_events,
        'hs_events': hs_events,
        'type': 'general'
    }

    return render(request, "event-list.html", context)
