from datetime import datetime
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.handlers.wsgi import WSGIRequest

from .models import *

# EC Positions
ec = ['President', 'Vice President', 'Vice President of Health and Safety', 'Secretary', 'Treasurer', 'Marshal',
      'Recruitment Chair', 'Scholarship Chair']
# Positions not on EC that have importance on the dashboard
non_ec = ['Service Chair', 'Philanthropy Chair', 'Detail Manager']

# Toggle dependant on whether you want position verification
# if os.environ.get('DEBUG'):
#     debug = os.environ.get('DEBUG')
# else:
#     debug = True
debug = False


def get_semester():
    semester = Semester.objects.filter(season=get_season(), year=get_year())
    if semester.exists():
        return semester[0]
    else:
        semester = Semester(season=get_season(), year=get_year())
        semester.save()
        return semester


# get semester used for filtering throughout the views
# based on SEASON_CHOICES in models (0,1,2) => ('Spring','Summer','Fall')
def get_season():
    # return '0'
    month = datetime.datetime.now().month
    if debug:
        return '0'
    else:
        if month <= 5:
            return '0'
        elif month <= 7:
            return '1'
        else:
            return '2'


def get_season_from(month):
    if month <= 5:
        return '0'
    elif month <= 7:
        return '1'
    else:
        return '2'


def get_year():
    return datetime.datetime.now().year


def get_month():
    return datetime.datetime.now().month


def get_day():
    return datetime.datetime.now().day


def forms_is_valid(form_list):
    for form in form_list:
        if not form.is_valid():
            return False
    return True


def do_verify(pos, user):
    if pos == 'ec' and Position.objects.get(brothers__user=user).ec:
        return True
    brothers = Position.objects.get(title=pos).brothers.all()
    if user.brother in brothers:
        return True
    return False


def verify_position(positions):
    def verify_decorator(f):
        def error(request):
            e = "Access denied. Only %s may access this page" % ", ".join(
                positions
            )
            messages.error(request, e)
            return HttpResponseRedirect(reverse('dashboard:home'))

        def wrapper(*args, **kwargs):
            request = None
            for a in args:
                if type(a) == WSGIRequest:
                    request = a
                    break

            for pos in positions:
                try:
                    # TODO: allow multiple brothers to hold a position
                    if do_verify(pos, request.user):
                        return f(*args, **kwargs)
                except AttributeError as e:
                    print(
                        'Warning: error when verifying position. Denying. '
                        'Error: %s' % e
                    )
                    return error(request)

            return error(request)

        return wrapper
    return verify_decorator


def verify_brother(brother, user):
    """ Verify user is the same as brother """
    return user.brother.id == brother.id
