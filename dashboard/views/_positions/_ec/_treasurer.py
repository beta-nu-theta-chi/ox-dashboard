from django.shortcuts import render

from dashboard.utils import verify_position

@verify_position(['Treasurer', 'President', 'Adviser'])
def treasurer(request):
    """ Renders all the transactional information on the site for the treasurer """
    return render(request, 'treasurer.html', {})
