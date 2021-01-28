from django.shortcuts import render

from dashboard.models import Position
from dashboard.utils import verify_position


@verify_position([Position.PositionChoices.TREASURER, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def treasurer(request):
    """ Renders all the transactional information on the site for the treasurer """
    return render(request, 'treasurer.html', {})
