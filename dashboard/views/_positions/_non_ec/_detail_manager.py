from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

import random
import datetime

from dashboard.forms import (
    CreateDetailGroups,
    DeleteDetailGroup,
    FinishSundayDetail,
    HouseDetailsSelectForm,
    SelectDate,
    SelectDetailGroups,
    SelectSemester,
    SuppliesFinishForm,
)
from dashboard.models import (
    Brother,
    DetailGroup,
    Position,
    SundayDetail,
    SundayGroupDetail,
    ThursdayDetail,
)
from dashboard.utils import (
    build_sunday_detail_email,
    build_thursday_detail_email,
    calc_fines,
    get_semester,
    verify_brother,
    verify_position
)


@verify_position(['Detail Manager', 'Adviser'])
def detail_m(request):
    """ Renders the detail manager page"""
    return render(request, 'detail-manager.html', {})


@verify_position(['Detail Manager', 'Adviser'])
def supplies_finish(request):
    form = SuppliesFinishForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            for supply in form.cleaned_data['choices']:
                supply.done = True
                supply.save()

    context = {
        'form': form,
        'button': 'Mark as Ordered'
    }
    return render(request, 'detail-manager-finish-supplies.html', context)


@verify_position(['Detail Manager', 'Adviser'])
@transaction.atomic
def house_detail_toggle(request):
    """Selects who does house details"""
    form = HouseDetailsSelectForm(request.POST or None)
    position = Position.objects.get(title='Detail Manager')

    if request.method == 'POST':
        if form.is_valid():
            brothers = Brother.objects.filter(brother_status='1')
            brothers.update(does_house_details=False)
            for c in ['does_details_part', 'doesnt_do_details_part']:
                brothers = form.cleaned_data[c]
                for b in brothers:
                    b.does_house_details = True
                    b.save()

    context = {
        'form': form,
        'position': position
    }
    return render(request, 'detail-manager-house-detail-toggle.html', context)


@verify_position(['Detail Manager', 'Adviser'])
@transaction.atomic
def create_groups(request):
    """Create detail groups for a specific semester. Decides how many to create
    based on the group size and brothers living in the house"""
    form = CreateDetailGroups(request.POST or None)
    position = Position.objects.get(title='Detail Manager')

    if request.method == 'POST':
        if form.is_valid():
            num_brothers = len(Brother.objects.filter(does_house_details=True))
            num_groups = int(num_brothers / form.cleaned_data['size'])

            for i in range(num_groups):
                g = DetailGroup(semester=form.cleaned_data['semester'])
                g.save()

            return HttpResponseRedirect(reverse('dashboard:select_groups'))

    context = {
        'form': form,
        'position': position
    }
    return render(request, 'detail-manager-create-groups.html', context)


@verify_position(['Detail Manager', 'Adviser'])
@transaction.atomic
def select_groups(request):
    """Select brothers in detail groups (for this semester)"""
    form = SelectDetailGroups(request.POST or None, semester=get_semester())
    position = Position.objects.get(title='Detail Manager')

    if request.method == 'POST':
        if form.is_valid():
            for gid, brothers in form.extract_groups():
                group = DetailGroup.objects.get(pk=int(gid))
                group.brothers = brothers
                group.save()

    context = {
        'form': form,
        'position': position
    }
    return render(request, 'detail-manager-select-groups.html', context)


@verify_position(['Detail Manager', 'Adviser'])
@transaction.atomic
def delete_groups(request):
    """Delete detail groups.  Can select a semester to delete form"""
    semester_form = SelectSemester(request.GET or None)
    if semester_form.is_valid():
        semester = semester_form.cleaned_data['semester']
    else:
        semester = get_semester()
    form = DeleteDetailGroup(request.POST or None, semester=semester)

    if request.method == 'POST':
        if form.is_valid():
            for g in form.cleaned_data['groups']:
                g.delete()

    context = {'form': form, 'semester_form': semester_form}

    return render(request, 'detail-manager-delete-groups.html', context)


@verify_position(['Detail Manager', 'Adviser'])
@transaction.atomic
def post_thursday(request):
    """Post Thursday Details, due on the date from the form"""
    date_form = SelectDate(request.POST or None)

    if request.method == 'POST':
        if date_form.is_valid():
            brothers = Brother.objects.filter(does_house_details=True)
            details = settings.THURSDAY_DETAILS

            bros = [b for b in brothers]
            brothers = bros
            random.shuffle(details)
            random.shuffle(brothers)

            matching = zip(brothers, details)
            assigned = []
            emails = []

            for (b, d) in matching:
                detail = ThursdayDetail(
                    short_description=d['name'],
                    long_description="\n".join(d['tasks']),
                    due_date=date_form.cleaned_data['due_date'], brother=b,
                )
                detail.save()
                assigned.append(detail)
                emails.append(
                    build_thursday_detail_email(
                        detail, request.scheme + "://" + request.get_host()
                    )
                )

            det_manager_email = Position.objects.get(
                title='Detail Manager'
            ).brothers.first().user.email
            for (subject, message, to) in emails:
                send_mail(subject, message, det_manager_email, to)

    context = {
        'form': date_form,
        'date': 'thursday',
    }
    return render(request, 'detail-manager-post-details.html', context)


# TODO: This might belong in the house management section.  Cannot check because details do not seem to work.
@login_required
def finish_thursday_detail(request, detail_id):
    """Marks a Thursday Detail as done, by either its owner or the detail
    manager"""
    detail = ThursdayDetail.objects.get(pk=detail_id)
    if not verify_brother(detail.brother, request.user):
        if request.user.brother not in Position.objects.get(
            title='Detail Manager'
        ).brothers.all():
            messages.error(request, "That's not your detail!")
            return HttpResponseRedirect(reverse('dashboard:home'))

    if request.method == 'POST' and not detail.done:
        detail.done = True
        detail.finished_time = datetime.datetime.now()
        detail.save()

    context = {'detail': detail}

    return render(request, 'finish-thursday-detail.html', context)


@verify_position(['Detail Manager', 'Adviser'])
@transaction.atomic
def post_sunday(request):
    """Post Sunday Details, due on the date from the form"""
    date_form = SelectDate(request.POST or None)

    if request.method == 'POST':
        if date_form.is_valid():
            groups = DetailGroup.objects.filter(semester=get_semester())
            details = settings.SUNDAY_DETAILS

            g = [e for e in groups]
            groups = g
            random.shuffle(groups)
            random.shuffle(details)

            emails = []

            for group in groups:
                if len(details) <= 0:
                    break
                group_detail = SundayGroupDetail(
                    group=group, due_date=date_form.cleaned_data['due_date']
                )
                group_detail.save()
                for _ in range(group.size()):
                    if len(details) <= 0:
                        break
                    d = details.pop()
                    det = SundayDetail(
                        short_description=d['name'],
                        long_description="\n".join(d['tasks']),
                        due_date=date_form.cleaned_data['due_date']
                    )
                    det.save()
                    group_detail.details.add(det)
                group_detail.save()
                emails.append(
                    build_sunday_detail_email(
                        group_detail,
                        request.scheme + "://" + request.get_host()
                    )
                )

            det_manager_email = Position.objects.get(
                title='Detail Manager'
            ).brothers.first().user.email
            for (subject, message, to) in emails:
                send_mail(subject, message, det_manager_email, to)

    context = {
        'form': date_form,
        'date': 'sunday',
    }
    return render(request, 'detail-manager-post-details.html', context)


# TODO: This might belong in the house management section.  Cannot check because details do not seem to work.
@login_required
def finish_sunday_detail(request, detail_id):
    groupdetail = SundayGroupDetail.objects.get(pk=detail_id)
    if request.user.brother not in groupdetail.group.brothers.all():
        if request.user.brother not in Position.objects.get(
            title='Detail Manager'
        ).brothers.all():
            messages.error(request, "That's not your detail!")
            return HttpResponseRedirect(reverse('dashboard:home'))

    form = FinishSundayDetail(request.POST or None, groupdetail=groupdetail)

    if request.method == 'POST':
        if form.is_valid():
            detail = form.cleaned_data['detail']
            detail.done = True
            detail.finished_time = datetime.datetime.now()
            detail.finished_by = request.user.brother
            detail.save()

    context = {
        'groupdetail': groupdetail,
        'details': groupdetail.details.all(),
        'form': form,
        'who': ", ".join(
            [str(b) for b in groupdetail.group.brothers.all()]
        ),
        'due': groupdetail.details.all()[0].due_date,
    }

    return render(request, 'finish-sunday-detail.html', context)


@verify_position(['Detail Manager', 'Adviser'])
def current_details_brother(request, brother_id):
    brother = Brother.objects.get(pk=brother_id)
    return current_details_helper(request, brother)


def current_details_helper(request, brother):
    if not brother.does_house_details:
        context = {
            'does_house_details': False,
            'who': str(brother),
        }
        return render(request, 'list-details.html', context)

    context = {}

    last_sunday = SundayGroupDetail.objects.filter(
        group__brothers=brother, group__semester=get_semester()
    ).order_by('-due_date').first()
    if last_sunday:
        context['last_sunday'] = last_sunday
        context['last_sunday_link'] = last_sunday.finish_link()
        context['sunday_text'] = "\n\n\n".join(
            [d.full_text() for d in last_sunday.details.all()]
        )

    last_thursday = ThursdayDetail.objects.filter(
        brother=brother
    ).order_by('-due_date').first()
    context['last_thursday'] = last_thursday
    context['last_thursday_link'] = last_thursday.finish_link()
    context['thursday_text'] = last_thursday.full_text()

    context['who'] = str(brother)
    context['does_house_details'] = True

    return render(request, 'list-details.html', context)


@verify_position(['Detail Manager', 'Adviser'])
def all_details_brother(request, brother_id):
    brother = Brother.objects.get(pk=brother_id)
    return all_details_helper(request, brother)


def all_details_helper(request, brother):
    if not brother.does_house_details:
        context = {
            'does_house_details': False,
            'who': str(brother),
        }
        return render(request, 'list-details.html', context)

    thursday_details = ThursdayDetail.objects.filter(brother=brother)

    sunday_group_details = SundayGroupDetail.objects.filter(
        group__brothers=brother, group__semester=get_semester()
    )

    context = {
        'thursday_details': thursday_details,
        'sunday_group_details': sunday_group_details,
        'does_house_details': True,
        'who': str(brother),
    }

    return render(request, 'all_details.html', context)


@verify_position(['Detail Manager', 'Adviser'])
def all_users_details(request):
    brothers = Brother.objects.filter(brother_status='1')
    b = {e: (
            reverse('dashboard:list_details_brother', args=[e.pk]),
            reverse('dashboard:all_details_brother', args=[e.pk]),
            reverse('dashboard:detail_fine_brother', args=[e.pk]),
            calc_fines(e)
    ) for e in brothers}
    context = {'brothers': b}
    return render(request, 'detail-manager-all-users-details.html', context)


@verify_position(['Detail Manager', 'Adviser'])
def detail_dates(request):
    semester_form = SelectSemester(request.GET or None)
    if semester_form.is_valid():
        semester = semester_form.cleaned_data['semester']
    else:
        semester = get_semester()

    thursday_dates = set([e.due_date for e in ThursdayDetail.objects.all()])
    thursday_dates = [
        (
            e, reverse('dashboard:details_on_date', args=[str(e)])
        ) for e in thursday_dates
    ]
    sunday_dates = set([e.due_date for e in SundayDetail.objects.all()])
    sunday_dates = [
        (
            e, reverse('dashboard:details_on_date', args=[str(e)])
        ) for e in sunday_dates
    ]

    context = {
        'semester_form': semester_form,
        'thursday_dates': thursday_dates,
        'sunday_dates': sunday_dates,
    }

    return render(request, 'detail-manager-details-by-date.html', context)


@verify_position(['Detail Manager', 'Adviser'])
def details_on_date(request, date):
    d_format = "%Y-%m-%d"
    date = datetime.datetime.strptime(date, d_format).date()
    thursday_details = ThursdayDetail.objects.filter(due_date=date)
    sunday_group_details = SundayGroupDetail.objects.filter(due_date=date)

    context = {
        'date': date,
        'thursday_details': thursday_details,
        'sunday_group_details': sunday_group_details,
    }

    return render(request, 'detail-manager-details-on-date.html', context)


@verify_position(['Detail Manager', 'Adviser'])
def detail_fines_brother(request, brother_id):
    brother = Brother.objects.get(pk=brother_id)
    return detail_fine_helper(request, brother)


def detail_fine_helper(request, brother):
    if not brother.does_house_details:
        context = {
            'does_house_details': False,
            'who': str(brother),
        }
        return render(request, 'list-details.html', context)

    fine = calc_fines(brother)

    context = {'fine': fine, 'brother': brother}

    return render(request, 'detail-fines.html', context)
