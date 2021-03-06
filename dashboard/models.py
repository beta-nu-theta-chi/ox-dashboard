import datetime
import os

import django.utils.timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Semester(models.Model):
    SEASON_CHOICES = (
        ('0', 'Spring'),
        ('1', 'Summer'),
        ('2', 'Fall'),
    )
    YEAR_CHOICES = []
    for r in range(2010, (datetime.datetime.now().year + 6)):
        YEAR_CHOICES.append((r, r))

    season = models.CharField(
        max_length=1,
        choices=SEASON_CHOICES,
        default='0',
    )
    year = models.IntegerField(
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year,
    )

    def __str__(self):
        return "%s - %s" % (self.year, self.get_season_display())


class Brother(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    # General profile information
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)

    class PronounChoices(models.TextChoices):
        FEMININE = "FEM", _("she/her/hers")
        MASCULINE = "MASC", _("he/him/his")
        NONBINARY = "NON", _("they/them/theirs")

    pronouns = models.CharField(max_length=4, choices=PronounChoices.choices, blank=True)
    roster_number = models.IntegerField(blank=True, null=True)
    semester_joined = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True
    )
    semester_graduating = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True, related_name='brother_graduating'
    )
    date_pledged = models.DateField(blank=True, null=True)

    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    FIFTH_YEAR = 'FY'
    ALUMNI = 'AL'

    SCHOOL_STATUS_CHOICES = (
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (FIFTH_YEAR, 'Fifth Year'),
        (ALUMNI, 'Alumni'),
    )
    school_status = models.CharField(
        max_length=2,
        choices=SCHOOL_STATUS_CHOICES,
        default=FRESHMAN,
    )

    BROTHER_STATUS_CHOICES = (
        ('0', 'Candidate'),
        ('1', 'Brother'),
        ('2', 'Alumni'),
    )

    brother_status = models.CharField(
        max_length=1,
        choices=BROTHER_STATUS_CHOICES,
        default='0',
    )

    # Secretary Information
    major = models.CharField(max_length=200, default="Undecided")
    minor = models.CharField(max_length=200, blank=True, null=True)
    case_ID = models.CharField(max_length=10)
    birthday = models.DateField()
    hometown = models.CharField(max_length=200, default="Cleveland, OH")
    t_shirt_size = models.CharField(max_length=5, default="M")

    # regex for proper phone number entry
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.")
    # validators should be a list
    phone_number = models.CharField(
        validators=[phone_regex], blank=True, max_length=15
    )

    # President Information
    emergency_contact = models.CharField(
        max_length=200, default="Chapter President"
    )
    emergency_contact_phone_number = models.CharField(
        validators=[phone_regex], blank=True, max_length=15
    )

    # Vice President Information
    room_number = models.CharField(max_length=3, default="NA")
    address = models.CharField(max_length=200, default="Theta Chi House")

    # Treasurer Information
    # TODO: Add treasury models

    # Recruitment Information
    # TODO: determine if there are any recruitment models

    # Service Chair Information
    # TODO: determine if there are any service models

    # Philanthropy Chair Information
    # TODO: determine if there are any philanthropy models

    # Detail Manager Chair Information
    # TODO: determine if there are any detail manager models
    does_house_details = models.BooleanField(default=False)
    does_kitchen_details = models.BooleanField(default=False)
    in_house = models.BooleanField(default=True)

    def __str__(self):
        return self.first_name + " " + self.last_name

    # returns the brother's attendance fraction for the associated event
    def get_attendance(self, event_type):
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year
        if month <= 5:
            season = '0'
        elif month <= 7:
            season = '1'
        else:
            season = '2'
        semester, _ = Semester.objects.get_or_create(season=season, year=year)
        return "%s / %s" % (
            event_type.objects.filter(semester=semester, mandatory=True, attendees_brothers=self).count() + event_type.objects.filter(
                semester=semester, mandatory=True, excuse__status=1).count(),
            event_type.objects.filter(semester=semester, mandatory=True, eligible_attendees=self, date__lt=datetime.datetime.now()).count()
        )

    def get_chapter_attendance(self):
        return self.get_attendance(ChapterEvent)

    def get_recruitment_attendance(self):
        return self.get_attendance(RecruitmentEvent)

    def get_hs_attendance(self):
        return self.get_attendance(HealthAndSafetyEvent)

    def get_philanthropy_attendance(self):
        return self.get_attendance(PhilanthropyEvent)

    def get_service_attendance(self):
        return self.get_attendance(ServiceEvent)


class MeetABrother(models.Model):
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE, related_name='brother_mab')
    candidate = models.ForeignKey(Brother, on_delete=models.CASCADE, related_name='candidate_mab')
    completed = models.BooleanField(default=False)
    week = models.DateField(default=django.utils.timezone.now)

    def __str__(self):
        return self.candidate.first_name + " " + self.candidate.last_name + " meeting with " + self.brother.first_name + " " + self.brother.last_name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['brother', 'candidate'], name='unique_meet_a_brother')
        ]


class OnlineMedia(models.Model):
    name = models.CharField(max_length=45, unique=True)
    icon = models.ImageField(upload_to='media_icons')

    def __str__(self):
        return "%s" % self.name


class MediaAccount(models.Model):
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE, related_name='media_accounts')
    media = models.ForeignKey(OnlineMedia, on_delete=models.CASCADE, related_name='media')
    username = models.CharField(max_length=45)
    profile_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return str(self.brother) + "'s " + str(self.media) + " Account"
    

class CampusGroup(models.Model):
    name = models.CharField(max_length=45)
    brothers = models.ManyToManyField(Brother, related_name='groups')

    def __str__(self):
        return "%s" % self.name


class Classes(models.Model):
    department = models.CharField(max_length=4)
    number = models.CharField(max_length=4)
    brothers = models.ManyToManyField(Brother, related_name='classes')

    def ordered_brother_set(self):
        return self.brothers.order_by('last_name', 'first_name')

    class Meta:
        verbose_name_plural = "Classes"

    def __str__(self):
        return "%s" % self.department + " " + str(self.number)


class Grade(models.Model):
    class GradeChoices(models.TextChoices):
        A = 'A'
        B = 'B'
        C = 'C'
        D = 'D'
        F = 'F'
        AP = 'P', "AP"

    grade = models.CharField(max_length=1, choices=GradeChoices.choices)
    class_taken = models.ForeignKey(Classes, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, related_name='grades', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['class_taken', 'brother'], name='unique_grade')
        ]


def query_positions_with_committee():
    choices = Q()
    for position in COMMITTEE_CHAIRS:
        choices = choices | Q(title=position)
    return choices


class Position(models.Model):
    # This is a list of possible options for each position. The first term is the name of the choice object. A list of
    # these can be called using PositionChoices.names. The second term is the value of the choices object, a list of
    # which you can get via PositionChoices.values. The values are written as slugs that serve as the url for each
    # position's main page. Since the title field gets set to the values options, you can use the title to redirect to
    # the main page using HTTPResponseRedirect('/' + title). Lastly the values in _() at the end are the labels or human
    # readable names of the choices. If nothing is set there, the label is automatically set from the name, in title
    # case with words separated by _. A list of labels can be found using PositionChoices.labels
    class PositionChoices(models.TextChoices):
        PRESIDENT = 'president',
        VICE_PRESIDENT = 'vice-president'
        VICE_PRESIDENT_OF_HEALTH_AND_SAFETY = 'vphs', _('Vice President of Health and Safety')
        SECRETARY = 'secretary'
        TREASURER = 'treasurer'
        MARSHAL = 'marshal'
        RECRUITMENT_CHAIR = 'recruitment-chair'
        SCHOLARSHIP_CHAIR = 'scholarship-chair'
        DETAIL_MANAGER = 'detail-manager'
        PHILANTHROPY_CHAIR = 'philanthropy-chair'
        PUBLIC_RELATIONS_CHAIR = 'pr-chair'
        SERVICE_CHAIR = 'service-chair'
        ALUMNI_RELATIONS_CHAIR = 'alumni-relations-chair'
        MEMBERSHIP_DEVELOPMENT_CHAIR = 'memdev-chair'
        SOCIAL_CHAIR = 'social-chair'
        COMMUNITY_STANDARDS_CHAIR = 'community-standards-chair'
        OX_ROAST_CHAIR = 'ox-roast-chair', _('OX Roast Chair')
        DAMAGE_CHAIR = 'damage-chair'
        GREEK_GAMES_CHAIR = 'greek-games-chair'
        HISTORIAN = 'historian'
        FIRST_GUARD = 'first-guard'
        SECOND_GUARD = 'second-guard'
        INTERNAL_CHANGE_CHAIR = 'internal-change-chair'
        STANDARDS_BOARD_JUSTICE = 'standards-board-justice'
        EXECUTIVE_COUNCIL_MEMBER_AT_LARGE = 'executive-council-member-at-large'
        HOUSE_MANAGER = 'house-manager'
        RISK_MANAGER = 'risk-manager'
        IFC_REP = 'ifc-rep', _('IFC Rep')
        AWARDS_CHAIR = 'awards-chair'
        FOOD_STEWARD = 'food-steward'
        ATHLETICS_CHAIR = 'athletics-chair'
        DASHBOARD_CHAIR = 'dashboard-chair'
        ADVISER = 'adviser'

    title = models.CharField(max_length=45, choices=PositionChoices.choices, unique=True, blank=False)

    def in_ec(self):
        return self.title in (
            EC_POSITIONS
        )

    brothers = models.ManyToManyField(Brother)

    def get_brothers(self):
        return ", ".join([str(e) for e in self.brothers.all()])

    def __str__(self):
        return str(self.PositionChoices(self.title).label)


EC_POSITIONS = (
    Position.PositionChoices.PRESIDENT,
    Position.PositionChoices.VICE_PRESIDENT,
    Position.PositionChoices.VICE_PRESIDENT_OF_HEALTH_AND_SAFETY,
    Position.PositionChoices.SECRETARY,
    Position.PositionChoices.TREASURER,
    Position.PositionChoices.MARSHAL,
    Position.PositionChoices.RECRUITMENT_CHAIR,
    Position.PositionChoices.SCHOLARSHIP_CHAIR,
)


COMMITTEE_CHAIRS = (
    Position.PositionChoices.VICE_PRESIDENT_OF_HEALTH_AND_SAFETY,
    Position.PositionChoices.RECRUITMENT_CHAIR,
    Position.PositionChoices.SCHOLARSHIP_CHAIR,
    Position.PositionChoices.PHILANTHROPY_CHAIR,
    Position.PositionChoices.PUBLIC_RELATIONS_CHAIR,
    Position.PositionChoices.ALUMNI_RELATIONS_CHAIR,
    Position.PositionChoices.MEMBERSHIP_DEVELOPMENT_CHAIR,
    Position.PositionChoices.SOCIAL_CHAIR
)

EVENT_CHAIRS = (
    Position.PositionChoices.VICE_PRESIDENT_OF_HEALTH_AND_SAFETY,
    Position.PositionChoices.SECRETARY,
    Position.PositionChoices.RECRUITMENT_CHAIR,
    Position.PositionChoices.PHILANTHROPY_CHAIR,
    Position.PositionChoices.SERVICE_CHAIR,
)


class Report(models.Model):
    is_officer = models.BooleanField(default=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, blank=True, null=True, related_name="reports")
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE, related_name="reports")
    information = models.TextField()


class PotentialNewMember(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45, blank=True, null=True)
    case_ID = models.CharField(max_length=10, blank=True, null=True)

    # regex for proper phone number entry
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], blank=True, null=True, max_length=15
    )
    # validators should be a list

    primary_contact = models.ForeignKey(
        Brother, on_delete=models.CASCADE, related_name="primary"
        )
    secondary_contact = models.ForeignKey(
        Brother, on_delete=models.CASCADE, blank=True, null=True,
        related_name="secondary"
    )
    tertiary_contact = models.ForeignKey(
        Brother, on_delete=models.CASCADE, blank=True, null=True,
        related_name="tertiary"
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.first_name + " " + self.last_name


class ServiceSubmission(models.Model):
    name = models.CharField(max_length=200, default="Service Event")
    description = models.TextField(default="I did the service thing")
    hours = models.IntegerField(default=0)
    date_applied = models.DateTimeField(default=django.utils.timezone.now)

    STATUS_CHOICES = (
        ('0', 'Pending'),
        ('1', 'Awaiting Approval'),
        ('2', 'Approved'),
        ('3', 'Denied'),
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='0',
    )

    date = models.DateField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Given separate section to prevent accidental viewing while in admin views
class ScholarshipReport(models.Model):
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    past_semester_gpa = models.DecimalField(
        max_digits=5, decimal_places=2, default=4.0
    )
    cumulative_gpa = models.DecimalField(
        max_digits=5, decimal_places=2, default=4.0
    )
    scholarship_plan = models.TextField(
        default="Scholarship plan has not been setup yet if you past semester "
                "GPA or cum GPA are below 3.0 you should "
                "setup a meeting to have this corrected"
    )

    def __str__(self):
        return "%s %s - %s %s" % (self.brother.first_name,
                                  self.brother.last_name,
                                  self.semester.get_season_display(),
                                  self.semester.year)


# method used to set the default for event.eligible_brothers
def all_actives_and_candidates():
    return Brother.objects.filter(brother_status__in=['0', '1'])


class TimeChoices(datetime.time, models.Choices):
    T_9 = 9, '9:00 A.M.'
    T_9_30 = 9,30, '9:30 A.M.'
    T_10 = 10, '10:00 A.M.'
    T_10_30 = 10, 30, '10:30 A.M.'
    T_11 = 11, '11:00 A.M.'
    T_11_30 = 11, 30, '11:30 A.M.'
    T_12 = 12, '12:00 P.M.'
    T_12_30 = 12, 30, '12:30 P.M.'
    T_13 = 13, '1:00 P.M.'
    T_13_30 = 13, 30, '1:30 P.M.'
    T_14 = 14, '2:00 P.M.'
    T_14_30 = 14, 30, '2:30 P.M.'
    T_15 = 15, '3:00 P.M.'
    T_15_30 = 15, 30, '3:30 P.M.'
    T_16 = 16, '4:00 P.M.'
    T_16_30 = 16, 30, '4:30 P.M.'
    T_17 = 17, '5:00 P.M.'
    T_17_30 = 17, 30, '5:30 P.M.'
    T_18 = 18, '6:00 P.M.'
    T_18_30 = 18, 30, '6:30 P.M.'
    T_19 = 19, '7:00 P.M.'
    T_19_30 = 19, 30, '7:30 P.M.'
    T_20 = 20, '8:00 P.M.'
    T_20_30 = 20, 30, '8:30 P.M.'
    T_21 = 21, '9:00 P.M.'
    T_21_30 = 21, 30, '9:30 P.M.'
    T_22 = 22, '10:00 P.M.'
    T_22_30 = 22, 30, '10:30 P.M.'
    T_23 = 23, '11:00 P.M.'
    T_23_30 = 23, 30, '11:30 P.M.'


class Event(models.Model):

    name = models.CharField(max_length=200, default="Event")
    date = models.DateField(default=django.utils.timezone.now)
    all_day = models.BooleanField(default=False)
    start_time = models.TimeField(default=datetime.time(hour=0, minute=0), choices=TimeChoices.choices)
    end_time = models.TimeField(blank=True, null=True, choices=TimeChoices.choices)
    attendees_brothers = models.ManyToManyField(Brother, blank=True)
    eligible_attendees = models.ManyToManyField(Brother, blank=False, related_name='+', default=all_actives_and_candidates)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    minutes = models.URLField(blank=True, null=True)
    mandatory = models.BooleanField(default=True)
    slug = models.SlugField(blank=True) # a field which stores the url to redirect to after running operations on the event

    def __str__(self):
        return self.name + " " + str(self.date)


def set_event_kwarg_defaults(kwargs, slug, name):
    if 'slug' not in kwargs:
        kwargs['slug'] = slug
    if 'name' not in kwargs:
        kwargs['name'] = name


class ChapterEvent(Event):

    def __str__(self):
        return "Chapter Event - " + str(self.date)

    def __init__(self, *args, **kwargs):
        set_event_kwarg_defaults(kwargs, Position.PositionChoices.SECRETARY, 'Chapter Event')
        super(ChapterEvent, self).__init__(*args, **kwargs)


class PhilanthropyEvent(Event):
    rsvp_brothers = models.ManyToManyField(
        Brother, blank=True, related_name="rsvp_philanthropy"
    )

    def __str__(self):
        return "Philanthropy Event - " + str(self.date)

    def __init__(self, *args, **kwargs):
        set_event_kwarg_defaults(kwargs, Position.PositionChoices.PHILANTHROPY_CHAIR, 'Philanthropy Event')
        super(PhilanthropyEvent, self).__init__(*args, **kwargs)


class ServiceEvent(Event):
    rsvp_brothers = models.ManyToManyField(
        Brother, blank=True, related_name="rsvp_service"
    )

    def __str__(self):
        return "Service Event - " + str(self.date)

    def __init__(self, *args, **kwargs):
        set_event_kwarg_defaults(kwargs, Position.PositionChoices.SERVICE_CHAIR, 'Service Event')
        super(ServiceEvent, self).__init__(*args, **kwargs)


class RecruitmentEvent(Event):
    attendees_pnms = models.ManyToManyField(PotentialNewMember, blank=True)
    rush = models.BooleanField(default=True)
    picture = models.ImageField(upload_to='recruitment', null=True)
    location = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Recruitment Event - " + str(self.date)

    def __init__(self, *args, **kwargs):
        set_event_kwarg_defaults(kwargs, Position.PositionChoices.RECRUITMENT_CHAIR, 'Recruitment Event')
        super(RecruitmentEvent, self).__init__(*args, **kwargs)


class HealthAndSafetyEvent(Event):
    def __str__(self):
        return "Health and Safety Event - " + str(self.date)

    def __init__(self, *args, **kwargs):
        set_event_kwarg_defaults(kwargs, Position.PositionChoices.VICE_PRESIDENT_OF_HEALTH_AND_SAFETY, 'Sacred Purpose Event')
        super(HealthAndSafetyEvent, self).__init__(*args, **kwargs)


class ScholarshipEvent(Event):
    def __str__(self):
        return "Scholarship Event - " + str(self.date)

    def __init__(self, *args, **kwargs):
        set_event_kwarg_defaults(kwargs, Position.PositionChoices.SCHOLARSHIP_CHAIR, 'Scholarship Event')
        super(ScholarshipEvent, self).__init__(*args, **kwargs)


def get_standing_committees(brother):
    committees = []
    for committee in brother.committee_set.all():
        if committee.in_standing():
            committees.append(committee.committee)
    return committees


def get_operational_committees(brother):
    committees = []
    for committee in brother.committee_set.all():
        if committee.in_operational():
            committees.append(committee.committee)
    return committees


class Committee(models.Model):
    class CommitteeChoices(models.TextChoices):
        ALUMNI_RELATIONS = 'AR'
        MEMBERSHIP_DEVELOPMENT = 'MD'
        PHILANTHROPY = 'PH'
        PUBLIC_RELATIONS = 'PR'
        RECRUITMENT = 'RE'
        SCHOLARSHIP = 'SC'
        SOCIAL = 'SO'
        HEALTH_AND_SAFETY = 'HS'

    STANDING_COMMITTEE_CHOICES = [
        ('PR', 'Public Relations'),
        ('RE', 'Recruitment'),
        ('SO', 'Social'),
        ('HS', 'Health and Safety'),
    ]

    OPERATIONAL_COMMITTEE_CHOICES = [
        ('AR', 'Alumni Relations'),
        ('MD', 'Membership Development'),
        ('PH', 'Philanthropy'),
        ('SC', 'Scholarship'),
    ]

    committee = models.CharField(max_length=2, choices=CommitteeChoices.choices, unique=True, blank=False)

    def in_standing(self):
        return self.committee in (x[0] for x in self.STANDING_COMMITTEE_CHOICES)

    def in_operational(self):
        return self.committee in (x[0] for x in self.OPERATIONAL_COMMITTEE_CHOICES)

    members = models.ManyToManyField(Brother, blank=True)

    chair = models.OneToOneField(Position, on_delete=models.PROTECT, limit_choices_to=query_positions_with_committee())

    class MeetingIntervals(models.IntegerChoices):
        WEEKLY = 7, 'Weekly'
        BIWEEKLY = 14, 'Biweekly'
        MONTHLY = 28, 'Monthly'

    meeting_interval = models.IntegerField(choices=MeetingIntervals.choices)

    MEETING_DAY = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    meeting_day = models.IntegerField(choices=MEETING_DAY)

    meeting_time = models.TimeField(choices=TimeChoices.choices)

    def __str__(self):
        return self.CommitteeChoices(self.committee).label


class CommitteeMeetingEvent(Event):
    committee = models.ForeignKey(Committee, on_delete=models.PROTECT, related_name='meetings')
    recurring = models.BooleanField(default=False)

    def __str__(self):
        return str(self.committee) + " - " + str(self.date)


class Excuse(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)
    date_submitted = models.DateField(default=django.utils.timezone.now)
    description = models.TextField(
        "Reasoning", default="I will not be attending because"
    )
    response_message = models.TextField(blank=True, null=True)

    STATUS_CHOICES = (
        ('0', 'Pending'),
        ('1', 'Approved'),
        ('2', 'Denied'),
        ('3', 'Non-Mandatory'),
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='0',
    )

    def __str__(self):
        return self.brother.first_name \
            + " " + self.brother.last_name + " - " + str(self.event.name)


class Supplies(models.Model):
    what = models.CharField(max_length=256)
    done = models.BooleanField(default=False)
    when = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Supplies"

    def __str__(self):
        return self.what


class DetailGroup(models.Model):
    """A detail group. Contains brothers and a semester"""
    brothers = models.ManyToManyField(Brother)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def size(self):
        return len(self.brothers.all())

    def __str__(self):
        return ", ".join([str(b) for b in self.brothers.all()])


class Detail(models.Model):
    """Abstract class for details"""
    short_description = models.CharField(max_length=64)
    long_description = models.TextField(null=False)
    done = models.BooleanField(default=False)
    due_date = models.DateField(null=False)
    finished_time = models.DateTimeField(null=True)

    def full_text(self):
        text = "%s\n----------\n" % self.short_description
        text += "%s\n----------\n" % self.long_description
        text += "Due: %s\n\n" % str(self.due_date)
        return text

    class Meta:
        abstract = True

    def __str__(self):
        return self.short_description


class ThursdayDetail(Detail):
    """A thursday detail.  Adds the brother who it's assigned to"""
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE, null=False)

    def finish_link(self):
        return reverse(
            'dashboard:finish_thursday', args=[self.pk]
        )

    def __str__(self):
        return str(self.due_date) + ": " +\
            super(ThursdayDetail, self).__str__()


class SundayDetail(Detail):
    """A single Sunday detail.  Keeps track of who marks it done"""
    finished_by = models.ForeignKey(Brother, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.due_date) + ": " +\
            super(SundayDetail, self).__str__()


class SundayGroupDetail(models.Model):
    """A group detail.  Contains a group and a number of SundayDetails"""
    group = models.ForeignKey(DetailGroup, on_delete=models.CASCADE)
    details = models.ManyToManyField(SundayDetail)
    due_date = models.DateField()

    def finish_link(self):
        return reverse(
            'dashboard:finish_sunday', args=[self.pk]
        )

    def done(self):
        done = True
        for detail in self.details.all():
            done = done and detail.done
        return done

    def __str__(self):
        return "%s: %s" % (
            self.due_date, ", ".join([str(d) for d in self.details.all()])
        )


class Photo(models.Model):
    photo = models.ImageField(upload_to='photos')

    def __str__(self):
        return os.path.basename(str(self.photo))


class MinecraftPhoto(models.Model):
    photo = models.ImageField(upload_to='minecraft')

    def __str__(self):
        return os.path.basename(str(self.photo))


class PhoneTreeNode(models.Model):
    brother = models.ForeignKey(Brother, on_delete=models.PROTECT, related_name='phone_tree_brother')
    notified_by = models.ForeignKey(Brother, on_delete=models.PROTECT, null=True, related_name='phone_tree_notified_by') # null is the root (ie president)

    def __str__(self):
        if self.brother.position_set.filter(title=Position.PositionChoices.PRESIDENT):
            return self.brother.first_name + " " + self.brother.last_name
        return self.brother.first_name + " " + self.brother.last_name + " notified by " + self.notified_by.first_name + " " + self.notified_by.last_name

