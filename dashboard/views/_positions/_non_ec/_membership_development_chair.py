from django.shortcuts import render

from dashboard.utils import committee_meeting_panel,verify_position

from dashboard.models import *


@verify_position([Position.PositionChoices.MEMBERSHIP_DEVELOPMENT_CHAIR, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def memdev_c(request):
    committee_meetings, context = committee_meeting_panel(Position.PositionChoices.MEMBERSHIP_DEVELOPMENT_CHAIR)
    print(query_positions_with_committee())

    return render(request, 'membership-development-chair.html', context)
