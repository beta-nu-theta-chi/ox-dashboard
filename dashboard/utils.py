from datetime import datetime
from urllib.parse import quote_plus

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest

from .forms import (
    BrotherAttendanceForm,
    ChapterEventForm,
    ServiceEventForm,
    HealthAndSafetyEventForm,
    PhilanthropyEventForm,
)
from .models import *


# Toggle dependant on whether you want position verification
# if os.environ.get('DEBUG'):
#     debug = os.environ.get('DEBUG')
# else:
#     debug = True
debug = False


def get_semester(current_date=datetime.datetime.now()):
    season = get_season(current_date)
    year = current_date.year

    semester, _ = Semester.objects.get_or_create(season=season, year=year)

    return semester


# get semester used for filtering throughout the views
# based on SEASON_CHOICES in models (0,1,2) => ('Spring','Summer','Fall')
def get_season(current_date=datetime.datetime.now()):
    # return '0'
    month = current_date.month
    return get_season_from(month)


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
    if pos == 'ec' and Position.objects.get(brothers__user=user).in_ec:
        return True
    brothers = Position.objects.get(title=pos).brothers.all()
    if user.brother in brothers:
        return True
    return False


def verify_position(positions):
    def verify_decorator(f):
        def error(request):
            e = "Access denied. Only %s may access this page" % ", ".join(
                [y for x, y in Position.PositionChoices.choices if x in positions]
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


def committee_meeting_panel(position_name):
    position = Position.objects.get(title=position_name)
    committee = position.committee
    committee_meetings = committee.meetings.all().filter(semester=get_semester()).order_by("start_time")\
                                                 .order_by("date")
    context = {
        'committee_meetings': committee_meetings,
        'position': position,
        'position_slug': position_name, # a slug is just a label containing only letters, numbers, underscores, or hyphens
        'committee': committee,
    }

    return committee_meetings, context


def verify_brother(brother, user):
    """ Verify user is the same as brother """
    return user.brother.id == brother.id


def build_thursday_detail_email(thursday_detail, host):
    """Builds an email (w/ subject) for a Thursday detail"""
    done_link = host + reverse(
        'dashboard:finish_thursday', args=[thursday_detail.pk]
    )
    det_managers = Position.objects.get(title="Detail Manager").brothers.all()
    to = [thursday_detail.brother.user.email]

    email = "Dear %s, \n\n\n" % thursday_detail.brother.first_name

    email += "Your detail is:\n\n"
    email += thursday_detail.full_text()

    email += "\n"
    email += "Please complete it by the required time on the due date and " + \
        "mark it done by midnight.\n\n"
    email += "Go to this link to mark it done: %s\n\n\n" % done_link

    email += "L&R&Cleaning\n--\n%s" % ", ".join([b.first_name for b in det_managers])

    subject = "[DETAILS] %s - %s" % (
        thursday_detail.due_date, thursday_detail.short_description
    )

    return subject, email, to


def build_sunday_detail_email(sunday_group_detail, host):
    brothers = sunday_group_detail.group.brothers.all()
    details = sunday_group_detail.details.all()
    due = details[0].due_date
    det_managers = Position.objects.get(title="Detail Manager").brothers.all()
    done_link = host + reverse(
        'dashboard:finish_sunday', args=[sunday_group_detail.pk]
    )
    to = [b.user.email for b in sunday_group_detail.group.brothers.all()]

    email = "Dear %s, \n\n\n" % ", ".join(
        [b.first_name for b in brothers.all()]
    )

    email += "Your Sunday details are:\n\n"
    for det in details:
        email += det.full_text()
        email += "\n"

    email += "Please complete them before the required time on the due " + \
        "date and make the ones you do as done by midnight.\n\n"
    email += "Go to this link to mark them done: %s\n\n\n" % done_link

    email += "L&R&Cleaning\n--\n%s" % ", ".join([b.first_name for b in det_managers])

    subject = "[DETAILS] Sunday details for %s" % due

    return subject, email, to


def fine_generator():
    x = 5
    while x < 25:
        yield x
        x += 5
    while True:
        yield x


def calc_fines_helper(num_missed):
    gen = fine_generator()
    f = 0
    for _ in range(num_missed):
        f += gen.next()

    return f


def calc_fines(brother):
    missed_thursday_num = len(ThursdayDetail.objects.filter(
        brother=brother, done=False, due_date__lt=datetime.datetime.now()
    ))

    sunday_group = DetailGroup.objects.filter(
        brothers=brother, semester=get_semester()
    )

    sunday_details = SundayGroupDetail.objects.filter(
        group=sunday_group, due_date__lt=datetime.datetime.now()
    )

    missed_sunday_num = len([e for e in sunday_details if not e.done()])

    fine = calc_fines_helper(missed_thursday_num + missed_sunday_num)

    return fine


def photo_context(photo_class):
    photo_urls = []
    for photo in photo_class.objects.all():
        photo_urls.append(photo.photo.url)

    context = {
        'photo_urls': photo_urls
    }

    return context


def photo_form(form_class, request):
    form = form_class(request.POST or None)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)

        # NOTE: If we move to a CDN instead of storing files with the server,
        # we can probably use this form, but not save the value (set form.save()
        # to form.save(commit=False)) and instead get the url or path from the returned
        # instance and then upload that file to the CDN
        if form.is_valid():
            # TODO: add error handling to stop user from uploading too many photos
            instance = form.save()
            return HttpResponseRedirect(reverse('dashboard:home'))

    return form


def attendance_list(request, event):
    """Creates a list of forms, 1 for each brother in eligible_attendees. Each form has 1 field, being a
    checkbox field to determine the attendance of the brother at the event with a label set to the brother's name
    prefix=counter ensures that in the html, the forms have different id's

    :param HttpRequest request:
        the request object for the view the resulting form list will be a part of
    :param Event event:
        the event object to create an attendance list for
    :returns:
        the list of brothers eligible to attend this event and the list of attendance forms, both listed in the same order
    :rtype: list[brothers], list[BrotherAttendanceForm]
    """
    brothers = event.eligible_attendees.all()
    brother_form_list = []

    for counter, brother in enumerate(brothers):
        new_form = BrotherAttendanceForm(request.POST or None, initial={'present':  event.attendees_brothers.filter(id=brother.id).exists()},
                                         prefix=counter,
                                         brother="- %s %s" % (brother.first_name, brother.last_name))
        brother_form_list.append(new_form)

    return brothers, brother_form_list


def semester_end_date(season, year, treat_summer_fall_as_same=True):
    """Calculate the last day of the semester given its season and year.

    The last day of the semester is the 31st of its ending month
    (May for Spring, July for Summer, December for Fall)

    :param str season:
        '0', '1', or '2' to represent Spring, Summer, or Fall respectively
    :param int year:
        The year of the semester to find the end date of
    :param bool treat_summer_fall_as_same:
        If true and summer is the season, it will be treated as though fall
        were given rather than summer
    :returns:
        the end date of the semester
    :rtype: datetime

    """
    # if spring semester, use may as the end month
    if season == '0':
        end_month = 5
    elif season == '1' and not treat_summer_fall_as_same:
        end_month = 7
    # otherwise, we are in the summer or fall semester, so use december as end month
    else:
        end_month = 12

    # last day of both May, July, and December is the 31st.
    last_day_of_month = 31

    return datetime.datetime(year, end_month, last_day_of_month)


def semester_start_date(season, year):
    """Calculate the start date of a semester given a season and year.

    The Start date of a semester is the first day of the month in which is starts
    (January for Spring, June for Summer, August for Fall)

    :param str season:
        '0', '1', or '2' to represent Spring, Summer, or Fall respectively
    :param int year:
        The year of the semester to find the start date of
    :returns:
        the start date of the semester
    :rtype: datetime

    """
    # Find the start month for the semester season
    start_month = {
        '0': 1,
        '1': 6,
        '2': 8
    }.get(season)

    start_day_of_month = 1

    return datetime.datetime(year, start_month, start_day_of_month)


def create_recurring_events(begin_date, day, interval, event_creator):
    """Create recurring events for the semester begin_date falls in.

    :param datetime begin_date:
        The earliest date at which an event could be scheduled.  Events are
        schedule only during the same semester as begin_date.
    :param int day:
        The integer day of the week on which the recurring events happen
    :param int interval:
        The number of day in between each event
    :param function event_creator:
        A function that takes (datetime, Semester) and creates an event.  The
        function does not need to return a value (any value returned is ignored).

    """
    date = begin_date
    semester = get_semester(date)

    # offset to next week if the weekday from day has already passed this week
    if date.weekday() >= day:
        date_offset = 7 + day - date.weekday()
    # otherwise use the weekday of this week matching day as the offset
    elif date.weekday() < day:
        date_offset = day - date.weekday()

    date = date + datetime.timedelta(days=date_offset)
    start_date = date
    end_date = semester_end_date(semester.season, date.year)

    day_count = int((end_date - start_date).days / interval) + 1
    for date in (start_date + datetime.timedelta(interval) * n for n in range(day_count)):
        event_creator(date, semester)


def create_committee_event(date, semester, meeting_time, committee_object):
    """Create a single committee meeting event for the given committee

    :param datetime date:
        The date of the committee meeting
    :param Semester semester:
        The semester in which the event occurs
    :param datetime.time meeting_time:
        The time of the day at which the meeting will occur
    :param Committee committee_object:
        The committee for which the event belongs to

    """
    event = CommitteeMeetingEvent(date=date, start_time=meeting_time, semester=semester,
                                  committee=committee_object, recurring=True)
    event.save()
    event.name = event.committee.get_committee_display() + " Committee Meeting"
    event.slug = event.committee.chair.title
    event.save()


def create_recurring_meetings(instance, committee):
    """Create recurring committee meetings for the given committee

    :param dict instance:
        a dictionary from a cleaned form (specifically CommitteeCreateForm)
        that defines the day of the week in 'meeting_day' on which meetings
        occur.  Additionally, the interval (or number of days between events) must be
        defined in 'meeting_interval'.  The time that the meeting should occur during the
        day shall be defined in 'meeting_time'
    :param str committee:
        The name of the committee to create recurring meetings for

    """
    committee_object = Committee.objects.get(committee=committee)

    create_recurring_events(
        datetime.datetime.now(),
        instance['meeting_day'],
        instance['meeting_interval'],
        lambda date, semester: create_committee_event(date, semester, instance['meeting_time'], committee_object))


def create_node_with_children(node_brother, notified_by, brothers_notified):
    PhoneTreeNode(brother=node_brother, notified_by=notified_by).save()

    for brother in brothers_notified:
        PhoneTreeNode(brother=brother, notified_by=node_brother).save()


def notifies(brother):
    return list(map(lambda node : node.brother, PhoneTreeNode.objects.filter(notified_by=brother)))


def notified_by(brother):
    node = PhoneTreeNode.objects.filter(brother=brother)
    return node[0].notified_by if len(node) > 0 else None


def create_attendance_list(events, excuses_pending, excuses_approved, brother):
    """zips together a list of tuples where the first element is each event and the second is the brother's
    status regarding the event. If the event hasn't occurred, the status is blank, if it's not a mandatory
    event it's 'not mandatory'

    :param list[Event] events:
        a list of events you want to create this attendance list for

    :param list[Event] excuses_pending:
        a list of events that the brother has excuses created for that are currently pending

    :param list[Event] excuses_approved:
        a list of events that the brother has excuses created for that are approved

    :param Brother brother:
        which brother the excuses are for

    :returns:
        a zipped list of events and its corresponding attendance
    :rtype: list[Event, str]

    """
    attendance = []
    for event in events:
        if event.date >= datetime.date.today():
            attendance.append('')
        elif not event.mandatory:
            attendance.append('Not Mandatory')
        else:
            if event.attendees_brothers.filter(id=brother.id):
                attendance.append('Attended')
            elif event.pk in excuses_approved:
                attendance.append('Excused')
            elif event.pk in excuses_pending:
                attendance.append('Pending')
            else:
                attendance.append('Unexcused')

    return zip(events, attendance)


def mark_attendance_list(brother_form_list, brothers, event):
    """Mark the attendance for the given brothers at the given event

    :param list[BrotherAttendanceForm] brother_form_list:
        a list of forms which holds the marked attendance for the brother it's associated with

    :param list[Brother] brothers:
        a list of brothers, values must correspond to the same order as it was used to create the brother_form_list

    :param Event event:
        the event that has its attendance being marked

    """
    for counter, form in enumerate(brother_form_list):
        instance = form.clean()
        if instance['present'] is True:
            event.attendees_brothers.add(brothers[counter])
            event.save()
            # if a brother is marked present, deletes any of the excuses associated with this brother and this event
            excuses = Excuse.objects.filter(brother=brothers[counter], event=event)
            if excuses.exists():
                for excuse in excuses:
                    excuse.delete()
        if instance['present'] is False:
            event.attendees_brothers.remove(brothers[counter])
            event.save()


def update_eligible_brothers(instance, event):
    # for each brother selected in the add brothers field, add them to eligible_attendees
    if instance['add_brothers']:
        event.eligible_attendees.add(*instance['add_brothers'].values_list('pk', flat=True))
    # for each brother selected in the add brothers field, remove them from eligible_attendees
    # and the attended brothers list
    if instance['remove_brothers']:
        event.eligible_attendees.remove(*[o.id for o in instance['remove_brothers']])
        event.attendees_brothers.remove(*[o.id for o in instance['remove_brothers']])
    event.save()


def save_event(instance, eligible_attendees):
    semester, created = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
                                      year=instance.date.year)
    instance.semester = semester
    instance.save()
    # you must save the instance into the database as a row in the table before you can set the manytomany field
    instance.eligible_attendees.set(eligible_attendees)


def get_human_readable_model_name(object):
    """When given any object, returns the human readable name of its class/model

    :param Class object:
        any object of any type to have its human readable name returned

    :returns:
        end_string
    :rtype: string

    """
    was_last_upper = True
    end_string = ''
    for char in object.__class__.__name__:
        if char.isupper():
            if not was_last_upper:
                end_string += ' ' + char
            else:
                end_string += char
            was_last_upper = True
        else:
            was_last_upper = False
            end_string += char

    return end_string


def get_form_from_position(position, request):
    """Using the title of the position, return the event form related to that position

    :param str position:
        the string holding the title of the position, written as its related slug

    :param HttpRequest request:
        the request object for the view the resulting form will be a part of

    :returns:
        the form related to position
    :rtype: Form

    """
    form_dict = {
        Position.PositionChoices.PHILANTHROPY_CHAIR: PhilanthropyEventForm(request.POST or None, initial={'name': 'Philanthropy Event'}),
        Position.PositionChoices.SECRETARY: ChapterEventForm(request.POST or None, initial={'name': 'Chapter Event'}),
        Position.PositionChoices.SERVICE_CHAIR: ServiceEventForm(request.POST or None, initial={'name': 'Service Event'}),
        Position.PositionChoices.VICE_PRESIDENT_OF_HEALTH_AND_SAFETY: HealthAndSafetyEventForm(request.POST or None, initial={'name': 'Sacred Purpose Event'}),
    }
    return form_dict[position]
