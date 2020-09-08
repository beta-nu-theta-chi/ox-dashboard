import datetime
import django.utils.timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.urls import reverse


class Semester(models.Model):
    SEASON_CHOICES = (
        ('0', 'Spring'),
        ('1', 'Summer'),
        ('2', 'Fall'),
    )
    YEAR_CHOICES = []
    for r in range(2010, (datetime.datetime.now().year + 2)):
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


def enumerated_choices(choices):
    enum_choices = set()

    for counter, choice in enumerate(choices):
        string_counter = str(counter)
        enum_choices.add((string_counter, choice))

    return enum_choices


class CommitteeMap:
    def __init__ (self, standing, operational):
        self.__standing_map = enumerated_choices(standing + ["Unassigned"])
        self.__operational_map = enumerated_choices(operational + ["Unassigned"])
        self.__combined_list = standing + operational
        self.__combined_map = enumerated_choices(self.__combined_list)
        self.__length_standing = len(standing)

    @property
    def standing_unassigned(self):
        return str(len(self.__standing_map) - 1)

    @property
    def operational_unassigned(self):
        return str(len(self.__operational_map) - 1)

    @property
    def standing_map(self):
        return self.__standing_map

    @property
    def operational_map(self):
        return self.__operational_map

    @property
    def combined_map(self):
        return self.__combined_map

    def committee_name(self, committee_id):
        return self.__combined_list(int(committee_id))

    def committee_id(self, committee_name):
        for counter, committee in enumerate(self.__combined_list):
            if committee == committee_name:
                return str(counter)
        return None

    def committee_mapping(self, committee_id):
        id_value = int(committee_id)
        if id_value >= self.__length_standing:
            return {'operational_committee' : str(id_value - self.__length_standing)}
        else:
            return {'standing_committee' : str(id_value)}

    def mapping_from_name(self, committee_name):
        return self.committee_mapping(self.committee_id(committee_name))


ALUMNI_RELATIONS = 'AR'
MEMBERSHIP_DEVELOPMENT = 'MD'
PHILANTHROPY = 'PH'
PUBLIC_RELATIONS = 'PR'
RECRUITMENT = 'RE'
SCHOLARSHIP = 'SC'
SOCIAL = 'SO'
HEALTH_AND_SAFETY = 'HS'
UNASSIGNED = 'NA'


class Brother(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    # General profile information
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    roster_number = models.IntegerField(blank=True, null=True)
    semester_joined = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True
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

    STANDING_COMMITTEE_CHOICES = [
        (PUBLIC_RELATIONS, 'Public Relations'),
        (RECRUITMENT, 'Recruitment'),
        (SOCIAL, 'Social'),
        (HEALTH_AND_SAFETY, 'Health and Safety'),
        (UNASSIGNED, 'Unassigned')
    ]

    OPERATIONAL_COMMITTEE_CHOICES = [
        (ALUMNI_RELATIONS, 'Alumni Relations'),
        (MEMBERSHIP_DEVELOPMENT, 'Membership Development'),
        (PHILANTHROPY, 'Philanthropy'),
        (SCHOLARSHIP, 'Scholarship'),
        (UNASSIGNED, 'Unassigned')
    ]

    standing_committee = models.CharField(max_length=2, choices=STANDING_COMMITTEE_CHOICES, default=UNASSIGNED)
    operational_committee = models.CharField(max_length=2, choices=OPERATIONAL_COMMITTEE_CHOICES, default=UNASSIGNED)

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


class Position(models.Model):
    title = models.CharField(max_length=45)
    ec = models.BooleanField(default=False)
    brothers = models.ManyToManyField(Brother, related_name='brothers')
    has_committee = models.BooleanField(default=False)

    def get_brothers(self):
        return ", ".join([str(e) for e in self.brothers.all()])

    def __str__(self):
        return self.title


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
        return (self.first_name + " " + self.last_name)


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


class Event(models.Model):
    name = models.CharField(max_length=200, default="Event")
    date = models.DateField(default=django.utils.timezone.now)
    all_day = models.BooleanField(default=False)
    start_time = models.TimeField(default=datetime.time(hour=0, minute=0))
    end_time = models.TimeField(blank=True, null=True)
    attendees_brothers = models.ManyToManyField(Brother, blank=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True
    )
    description = models.TextField(blank=True, null=True)
    minutes = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class ChapterEvent(Event):
    mandatory = models.BooleanField(default=True)


class PhilanthropyEvent(Event):
    rsvp_brothers = models.ManyToManyField(
        Brother, blank=True, related_name="rsvp_philanthropy"
    )


class ServiceEvent(Event):
    rsvp_brothers = models.ManyToManyField(
        Brother, blank=True, related_name="rsvp_service"
    )


class RecruitmentEvent(Event):
    attendees_pnms = models.ManyToManyField(PotentialNewMember, blank=True)
    rush = models.BooleanField(default=True)
    picture = models.ImageField(upload_to='recruitment', null=True)
    location = models.TextField(blank=True, null=True)


class HealthAndSafetyEvent(Event):
    pass


class ScholarshipEvent(Event):
    pass


class StudyTableEvent(Event):
    def __str__(self):
        return "Study Tables - %s" % self.date


class Committee(models.Model):
    COMMITTEE_CHOICES = [
        (ALUMNI_RELATIONS, 'Alumni Relations'),
        (MEMBERSHIP_DEVELOPMENT, 'Membership Development'),
        (PHILANTHROPY, 'Philanthropy'),
        (PUBLIC_RELATIONS, 'Public Relations'),
        (RECRUITMENT, 'Recruitment'),
        (SCHOLARSHIP, 'Scholarship'),
        (SOCIAL, 'Social'),
        (HEALTH_AND_SAFETY, 'Health and Safety'),
    ]
    committee = models.CharField(max_length=2, choices=COMMITTEE_CHOICES, unique=True)
    STANDING = 'S'
    OPERATIONAL = 'O'
    TYPE_CHOICES = [
        (STANDING, 'Standing'),
        (OPERATIONAL, 'Operational')
    ]
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    members = models.ManyToManyField(Brother, blank=True)
    chair = models.OneToOneField(Position, on_delete=models.PROTECT, limit_choices_to={'has_committee': True})

    class MeetingTimes(datetime.timedelta, models.Choices):
        WEEKLY = 168, 'Weekly'
        BIWEEKLY = 336, 'Biweekly'
        MONTHLY = 672, 'Monthly'

    meeting_time = models.DurationField(blank=True, choices=MeetingTimes.choices)


class CommitteeMeetingEvent(Event):
    committee = models.ForeignKey(Committee, on_delete=models.PROTECT)


class Excuse(models.Model):
    event = models.ForeignKey(ChapterEvent, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(default=django.utils.timezone.now)
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
            + " " + self.brother.last_name + " - " + self.event.name


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

class MinecraftPhoto(models.Model):
    photo = models.ImageField(upload_to='minecraft')
