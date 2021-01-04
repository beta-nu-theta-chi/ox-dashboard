from django.shortcuts import render

from dashboard.utils import committee_meeting_panel, verify_position

@verify_position(['Social Chair', 'Vice President', 'President', 'Adviser'])
def social_c(request):
    committee_meetings, context = committee_meeting_panel('Social Chair')

    return render(request, 'social-chair.html', context)
