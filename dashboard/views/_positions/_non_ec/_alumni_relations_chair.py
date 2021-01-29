from django.shortcuts import render

from dashboard.models import Position
from dashboard.utils import committee_meeting_panel, verify_position


@verify_position([Position.PositionChoices.ALUMNI_RELATIONS_CHAIR, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def alumni_relations_c(request):
    committee_meetings, context = committee_meeting_panel(Position.PositionChoices.ALUMNI_RELATIONS_CHAIR)

    return render(request, 'alumni-relations-chair.html', context)
