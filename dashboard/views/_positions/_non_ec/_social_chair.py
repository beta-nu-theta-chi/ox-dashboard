from django.shortcuts import render

from dashboard.models import Position
from dashboard.utils import committee_meeting_panel, verify_position


@verify_position([Position.PositionChoices.SOCIAL_CHAIR, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def social_c(request):
    committee_meetings, context = committee_meeting_panel(Position.PositionChoices.SOCIAL_CHAIR)

    return render(request, 'social-chair.html', context)
