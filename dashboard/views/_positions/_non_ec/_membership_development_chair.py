from django.shortcuts import render

from dashboard.utils import committee_meeting_panel,verify_position

@verify_position(['Membership Development Chair', 'Vice President', 'President', 'Adviser'])
def memdev_c(request):
    committee_meetings, context = committee_meeting_panel('Membership Development Chair')

    return render(request, 'membership-development-chair.html', context)
