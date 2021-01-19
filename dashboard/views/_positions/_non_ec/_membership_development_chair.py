from django.shortcuts import render

from dashboard.utils import committee_meeting_panel,verify_position

from dashboard.models import *


@verify_position(['memdev-chair', 'vice-president', 'president', 'adviser'])
def memdev_c(request):
    committee_meetings, context = committee_meeting_panel('memdev-chair')
    print(query_positions_with_committee())

    return render(request, 'membership-development-chair.html', context)
