from django.shortcuts import render

from dashboard.forms import PhotoForm
from dashboard.models import Position
from dashboard.utils import committee_meeting_panel, photo_form, verify_position


@verify_position([Position.PositionChoices.PUBLIC_RELATIONS_CHAIR, Position.PositionChoices.RECRUITMENT_CHAIR, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def public_relations_c(request):
    committee_meetings, context = committee_meeting_panel(Position.PositionChoices.PUBLIC_RELATIONS_CHAIR)
    context.update({
        'form': photo_form(PhotoForm, request),
        'button': 'Add Photo'
    })

    return render(request, 'public-relations-chair.html', context)
