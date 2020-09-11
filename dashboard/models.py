import datetime
import django.utils.timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.urls import reverse
from django import forms


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
    class PositionChoices(models.TextChoices):
        PRESIDENT = 'President'
        VICE_PRESIDENT = 'Vice President'
        VPHS = 'Vice President of Health and Safety'
        SECRETARY = 'Secretary'
        TREASURER = 'Treasurer'
        MARSHAL = 'Marshal'
        RECRUITMENT_CHAIR = 'Recruitment Chair'
        SCHOLARSHIP_CHAIR = 'Scholarship Chair'
        DETAIL_MANAGER = 'Detail Manager'
        PHILANTHROPY_CHAIR = 'Philanthropy Chair'
        PUBLIC_RELATIONS_CHAIR = 'Public Relations Chair'
        SERVICE_CHAIR = 'Service Chair'
        ALUMNI_RELATIONS_CHAIR = 'Alumni Relations Chair'
        MEMBERSHIP_DEVELOPMENT_CHAIR = 'Membership Development Chair'
        SOCIAL_CHAIR = 'Social Chair'
        ADVISER = 'Adviser'

    title = models.CharField(max_length=45, choices=PositionChoices.choices, unique=True)

    def in_ec(self):
        return self.title in (
            'President',
            'Vice President',
            'Vice President of Health and Safety',
            'Secretary',
            'Treasurer',
            'Marshal',
            'Recruitment Chair',
            'Scholarship Chair',
        )

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

    name = models.CharField(max_length=200, default="Event")
    date = models.DateField(default=django.utils.timezone.now)
    all_day = models.BooleanField(default=False)
    start_time = models.TimeField(default=datetime.time(hour=0, minute=0), choices=TimeChoices.choices)
    end_time = models.TimeField(blank=True, null=True, choices=TimeChoices.choices)
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


def get_committees(brother):
    committees = []
    for committee in Committee.objects.all():
        if brother in committee.members.all():
            committees.append(committee.committee)
    return committees


def get_standing_committees(brother):
    committees = []
    for committee in Committee.objects.all():
        if brother in committee.members.all() and committee.in_standing():
            committees.append(committee.committee)
    return committees


def get_operational_committees(brother):
    committees = []
    for committee in Committee.objects.all():
        if brother in committee.members.all() and committee.in_operational():
            committees.append(committee.committee)
    return committees


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

    STANDING_COMMITTEE_CHOICES = [
        (PUBLIC_RELATIONS, 'Public Relations'),
        (RECRUITMENT, 'Recruitment'),
        (SOCIAL, 'Social'),
        (HEALTH_AND_SAFETY, 'Health and Safety'),
    ]

    OPERATIONAL_COMMITTEE_CHOICES = [
        (ALUMNI_RELATIONS, 'Alumni Relations'),
        (MEMBERSHIP_DEVELOPMENT, 'Membership Development'),
        (PHILANTHROPY, 'Philanthropy'),
        (SCHOLARSHIP, 'Scholarship'),
    ]

    committee = models.CharField(max_length=2, choices=COMMITTEE_CHOICES, unique=True)

    def in_standing(self):
        return self.committee in (x[0] for x in self.STANDING_COMMITTEE_CHOICES)

    def in_operational(self):
        return self.committee in (x[0] for x in self.OPERATIONAL_COMMITTEE_CHOICES)

    members = models.ManyToManyField(Brother, blank=True)

    chair = models.OneToOneField(Position, on_delete=models.PROTECT, limit_choices_to={'has_committee': True})

    class MeetingIntervals(models.IntegerChoices):
        WEEKLY = 7, 'Weekly'
        BIWEEKLY = 14, 'Biweekly'
        MONTHLY = 28, 'Monthly'

    meeting_interval = models.IntegerField(choices=MeetingIntervals.choices, blank=True, null=True)

    MEETING_DAY = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    meeting_day = models.IntegerField(choices=MEETING_DAY, blank=True, null=True)

    class MeetingTime(datetime.time, models.Choices):
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

    meeting_time = models.TimeField(choices=MeetingTime.choices, blank=True)


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
