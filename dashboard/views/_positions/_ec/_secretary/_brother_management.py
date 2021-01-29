from django.shortcuts import render

from dashboard.models import Brother, Position
from dashboard.utils import verify_position


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def secretary_brother_list(request):
    """ Renders the Secretary way of viewing brothers """
    brothers = Brother.objects.exclude(brother_status='2')
    context = {
        'position': Position.objects.get(title=Position.PositionChoices.SECRETARY),
        'brothers': brothers
    }
    return render(request, "secretary/brother-list.html", context)
