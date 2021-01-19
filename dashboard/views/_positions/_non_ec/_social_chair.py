from django.shortcuts import render

from dashboard.utils import committee_meeting_panel, verify_position


@verify_position(['social-chair', 'vice-president', 'president', 'adviser'])
def social_c(request):
    committee_meetings, context = committee_meeting_panel('social-chair')

    return render(request, 'social-chair.html', context)
