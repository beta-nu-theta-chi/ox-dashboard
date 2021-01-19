from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

import datetime
import random

from dashboard.forms import (
    BrotherForm,
    BrotherEditForm,
    MABEditCandidateForm,
    MeetABrotherEditForm,
    MeetABrotherForm,
)
from dashboard.models import (
    Brother,
    ChapterEvent,
    Excuse,
    MeetABrother,
    User,
)
from dashboard.utils import forms_is_valid, get_semester, verify_position

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['marshal', 'vice-president', 'president', 'adviser'])
def marshal(request):
    """ Renders the marshal page listing all the candidates and relevant information to them """
    candidates = Brother.objects.filter(brother_status='0').order_by("last_name", "first_name")
    events = ChapterEvent.objects.filter(semester=get_semester()).exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []
    randomized_list = request.session.pop('randomized_list', None)

    mab_form_list = []

    for counter, candidate in enumerate(candidates):
        assigned_mab = MeetABrother.objects.filter(candidate=candidate).values_list('brother', flat=True)
        eligible_brothers = Brother.objects.filter(brother_status=1).exclude(pk__in=assigned_mab).order_by('last_name', 'first_name')
        form = MeetABrotherForm(request.POST or None, prefix=counter+1, candidate=candidate.first_name + ' ' + candidate.last_name)
        mab_form_list.append(form)
        if randomized_list is not None or []:
            form.fields['assigned_brother1'].initial = randomized_list[counter][0]
            form.fields['assigned_brother2'].initial = randomized_list[counter][1]
            form.fields['randomize'].initial = randomized_list[counter][2]
        else:
            form.fields['randomize'].initial = True
        form.fields['assigned_brother1'].queryset = eligible_brothers
        form.fields['assigned_brother2'].queryset = eligible_brothers

    for candidate in candidates:
        events_excused = 0
        events_unexcused = 0
        if candidate.date_pledged:
            expected_events = events.exclude(date_pledged__lt=datetime.date.today())
        else:
            expected_events = events
        for event in expected_events:
            if not event.attendees_brothers.filter(id=candidate.id).exists():
                if excuses.filter(brother=candidate, event=event).exists():
                    events_excused += 1
                else:
                    events_unexcused += 1
        events_excused_list.append(events_excused)
        events_unexcused_list.append(events_unexcused)

    candidate_attendance = zip(candidates, events_excused_list, events_unexcused_list)

    if request.method == 'POST':
        if 'submit' in request.POST:
            if forms_is_valid(mab_form_list):
                for counter, form in enumerate(mab_form_list):
                    instance = form.cleaned_data
                    if instance['assigned_brother1']:
                        mab1 = MeetABrother(candidate=candidates[counter], brother=instance['assigned_brother1'])
                        mab1.save()
                    if instance['assigned_brother2']:
                        mab2 = MeetABrother(candidate=candidates[counter], brother=instance['assigned_brother2'])
                        mab2.save()
                return HttpResponseRedirect(reverse('dashboard:meet_a_brother'))
        if 'randomize' in request.POST:
            if forms_is_valid(mab_form_list):
                randomized_list = []
                random1 = []
                random2 = []
                for form in mab_form_list:
                    instance = form.cleaned_data
                    if instance['randomize']:
                        queryset1 = form.fields['assigned_brother1'].queryset
                        queryset2 = queryset1
                        if queryset1.exists():
                            random1 = random.choices(queryset1, k=1)[0].pk
                            queryset2 = queryset1.exclude(pk=random1)
                        if queryset2.exists():
                            random2 = random.choices(queryset2, k=1)[0].pk
                        randomized_list.append((random1, random2, True))
                    else:
                        if instance['assigned_brother1']:
                            random1 = instance['assigned_brother1'].pk
                        else:
                            random1 = []
                        if instance['assigned_brother2']:
                            random2 = instance['assigned_brother2'].pk
                        else:
                            random2 = []
                        randomized_list.append((random1, random2, instance['randomize']))
                request.session['randomized_list'] = randomized_list
                return HttpResponseRedirect(reverse('dashboard:marshal'))

    context = {
        'candidates': candidates,
        'candidate_attendance': candidate_attendance,
        'mab_form_list': mab_form_list,
    }
    return render(request, 'marshal/marshal.html', context)


def marshal_mab_edit_candidate(request):
    initial = {'candidate': request.session.pop('candidate', None)}
    form = MABEditCandidateForm(request.POST or None, initial=initial)

    if request.method == 'POST':
        if form.is_valid():
            request.session['candidate'] = form.cleaned_data['candidate'].pk
            return HttpResponseRedirect(reverse('dashboard:marshal_mab_edit'))

    context = {
        'form': form,
    }

    return render(request, 'marshal/mab-edit-candidate.html', context)


def marshal_mab_edit(request):
    candidate = Brother.objects.get(pk=request.session.get('candidate', None))
    check_all = request.session.pop('check_all', False)

    mab_form_list = []

    brothers = Brother.objects.filter(brother_status='1')

    arbitrary_date_before_time = datetime.datetime(1000, 1, 1)

    for counter, brother in enumerate(brothers):
        form = MeetABrotherEditForm(request.POST or None, prefix=counter+1, brother=brother.pk, mab_exists=MeetABrother.objects.filter(brother=brother, candidate=candidate).exists())
        if check_all:
            form.fields['update'].initial = True
        mab_form_list.append(form)

    if request.method == 'POST':
        if 'submit' in request.POST:
            if forms_is_valid(mab_form_list):
                for counter, form in enumerate(mab_form_list):
                    instance = form.cleaned_data
                    if instance['update'] is True: #the user checked yes on this pairing of meet a brother, meaning we need to create a new one if it doesn't yet exist
                        mab, created = MeetABrother.objects.get_or_create(candidate=candidate, brother=brothers[counter], defaults={'completed':True, 'week':arbitrary_date_before_time})
                        if created: #if a new meet a brother is created we need to save it
                            mab.save()
                    elif instance['update'] is False: #the user has not checked yes on this pairing of meet a brother
                        # we need to delete this meet a brother if it exists
                        try: #get the meet a brother and delete it if it finds it
                            MeetABrother.objects.get(candidate=candidate, brother=brothers[counter]).delete()
                        except MeetABrother.DoesNotExist: #get will return this exception if it doesn't find one so just continue if it's not found
                            continue
                    else:
                        pass # instance['update'] is null
        if 'check_all' in request.POST:
            request.session['check_all'] = True
            return HttpResponseRedirect(reverse('dashboard:marshal_mab_edit'))
        if 'go_back' in request.POST:
            return HttpResponseRedirect(reverse('dashboard:marshal_mab_edit_candidate'))

    context = {
        'candidate': candidate,
        'mab_form_list': mab_form_list,
    }

    return render(request, 'marshal/mab-edit.html', context)


@verify_position(['marshal', 'vice-president', 'president', 'adviser'])
def marshal_candidate(request, brother_id):
    """ Renders the marshal page to view candidate info """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother,
        'position': 'Marshal',
    }
    return render(request, "brother-view.html", context)


@verify_position(['marshal', 'vice-president', 'president', 'adviser'])
def marshal_candidate_add(request):
    """ Renders the Marshal way of viewing a candidate """
    form = BrotherForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            user = User.objects.create_user(instance['case_ID'], instance['case_ID'] + "@case.edu",
                                            instance['password'])
            user.last_name = instance['last_name']
            user.save()

            brother = form.save(commit=False)
            brother.user = user
            brother.save()
            return HttpResponseRedirect(reverse('dashboard:marshal'))

    context = {
        'title': 'Add New Candidate',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class CandidateEdit(DashboardUpdateView):
    @verify_position(['marshal', 'vice-president', 'president', 'adviser'])
    def get(self, request, *args, **kwargs):
        return super(CandidateEdit, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:marshal')
    form_class = BrotherEditForm


class CandidateDelete(DashboardDeleteView):
    @verify_position(['marshal', 'vice-president', 'president', 'adviser'])
    def get(self, request, *args, **kwargs):
        return super(CandidateDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'generic-forms/base-confirm-delete.html'
    success_url = reverse_lazy('dashboard:marshal')
