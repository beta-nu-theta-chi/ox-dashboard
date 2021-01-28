from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

import datetime

from dashboard.forms import SelectSemester
from dashboard.models import (
    Brother,
    ChapterEvent,
    Committee,
    Event,
    MeetABrother,
    PhoneTreeNode,
    Position,
    Semester,
    TimeChoices,
    ec_positions,
)
from dashboard.utils import (
    create_node_with_children,
    create_recurring_events,
    semester_start_date,
    verify_position,
)


@verify_position([Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def president(request):
    """ Renders the President page and all relevant information """
    return render(request, 'president.html', {'semester_picker': SelectSemester()})


@verify_position([Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def create_phone_tree(request):
    """Creates the new phone tree and redirects to to the phone tree view."""
    # delete the exiting phone tree
    PhoneTreeNode.objects.all().delete()

    # Should only ever have 1 of each EC position
    president = Brother.objects.filter(position_title=Position.PositionChoices.PRESIDENT)[0]
    marshal = Brother.objects.filter(position_title=Position.PositionChoices.MARSHAL)[0]

    # get all the EC brothers that are not the president nor marshal
    standard_ec_brothers = Brother.objects.\
        filter(position__title__in=[x for x in ec_positions if x not in
                                    [Position.PositionChoices.PRESIDENT, Position.PositionChoices.MARSHAL]])

    all_ec_brothers = standard_ec_brothers + [president, marshal]

    non_ec_actives = Brother.objects.filter(brother_status='1').exclude(pk__in=all_ec_brothers)

    candidates = Brother.objects.filter(brother_status='0')

    # president's child nodes are implicitly created by the node creation functions below
    PhoneTreeNode(brother=president).save()

    create_node_with_children(marshal, president, candidates)

    actives_index = 0
    num_non_ec = non_ec_actives.count()
    num_standard_ec = standard_ec_brothers.count
    actives_per_ec_member = int(num_non_ec / num_standard_ec)
    remainder_actives = num_non_ec % num_standard_ec

    # assign brothers to all non-marshal and non president EC members
    for ec_member in standard_ec_brothers:
        # the remaining brothers that do no divide evenly into the total non ec actives
        # need to be distributed among EC as equally as possible
        if remainder_actives > 0:
            actives_to_assign = actives_per_ec_member + 1
            remainder_actives = remainder_actives - 1
        else:
            actives_to_assign = actives_per_ec_member

        # get the brothers to be assigned to the current ec_member
        assigned_actives = non_ec_actives[actives_index:actives_index + actives_to_assign]
        actives_index = actives_index + actives_to_assign

        # assign the brothers to the current ec_member
        create_node_with_children(ec_member, president, assigned_actives)

    return HttpResponseRedirect(reverse('dashboard:emergency_phone_tree_view'))


def __delete_all_meet_a_brothers():
    """Clear the Meet A Brother Table."""
    MeetABrother.objects.all().delete()


def __delete_old_events(semester):
    """Delete all events that occur before the given semester.

    :param Semester semester:
        The reference semester to delete events before it

    """
    current_date = datetime.datetime.now()
    start_date = semester_start_date(semester.season, semester.year)
    old_events = Event.objects.filter(date__lt=start_date)

    old_events.delete()


def __create_unmade_valid_semesters():
    """Create all possible semesters from the Semester Model choice Fields."""
    for year, _ in Semester.YEAR_CHOICES:
        for season, _ in Semester.SEASON_CHOICES:
            if not Semester.objects.filter(season=season, year=year).exists():
                sem = Semester()
                sem.year = year
                sem.season = season
                sem.save()


def __create_chapter_events(semester):
    """Create all the chapter events for the given semester.

    Chapter is at 6:30 every Sunday during the semester.  Currently, this
    will start on the first Sunday of the first month of the given semester
    (January for Spring, June for Summer, August for Fall)

    :param Semester semester:
        the semester to create chapter events for

    """
    sunday = 6

    create_recurring_events(
        semester_start_date(semester.season, semester.year),
        sunday,
        Committee.MeetingIntervals.WEEKLY,
        lambda date, semester: ChapterEvent(
            name="Chapter {}".format(date.date()),
            date=date,
            start_time=TimeChoices.T_18_30,  # 6:30 PM
            end_time=TimeChoices.T_20_30,  # 8:30 PM
            semester=semester,
        ).save())


@verify_position([Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def cleanup_semester(request):

    if request.method == 'POST':
        form = SelectSemester(request.POST)

        if form.is_valid():
            semester = form.cleaned_data['semester']

            __delete_all_meet_a_brothers()
            __delete_old_events(semester)
            __create_unmade_valid_semesters()
            __create_chapter_events(semester)

    # TODO: add error handling for false cases?

    return HttpResponseRedirect(reverse('dashboard:home'))
