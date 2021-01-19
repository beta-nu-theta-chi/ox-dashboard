from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

import datetime

from dashboard.models import (
    Brother,
    Committee,
    CommitteeMeetingEvent,
    Position,
)
from dashboard.forms import CommitteeForm, InHouseForm
from dashboard.utils import (
    forms_is_valid,
    get_operational_committees,
    get_semester,
    get_standing_committees,
    verify_position
)


@verify_position(['vice-president', 'president', 'adviser'])
def vice_president(request):
    """ Renders the Vice President page and all relevant information, primarily committee related """
    committee_meetings = CommitteeMeetingEvent.objects.filter(semester=get_semester())\
        .order_by("start_time").order_by("date")
    committees = Committee.objects.all()

    context = {
        'position': 'Vice President',
        'committees': committees,
        'committee_meetings': committee_meetings,
    }

    return render(request, 'vice-president/vice-president.html', context)


@verify_position(['vice-president', 'president', 'adviser'])
def vice_president_committee_assignments(request):
    """Renders Committee assignment update page for the Vice President"""
    form_list = []
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name', 'first_name')
    for brother in brothers:
        new_form = CommitteeForm(request.POST or None,
                                 initial={'standing_committees': get_standing_committees(brother),
                                          'operational_committees': get_operational_committees(brother)},
                                 prefix=brother.id)
        form_list.append(new_form)

    brother_forms = zip(brothers, form_list)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            meeting_map = {}
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                # since the form was created in the same order that the brothers are ordered in you can just use
                # counter to get the brother associated with the form
                brother = brothers[counter]
                # all the committees the brother was a part of before new committees were assigned
                brother_committees = get_standing_committees(brother) + get_operational_committees(brother)
                # unassigns the brother from all of their committees
                brother.committee_set.clear()
                # list of the committees the brother was now assigned to as strings representing the committees
                chosen_committees = instance['standing_committees'] + instance['operational_committees']
                # all committee options
                committee_choices = [x for x,y in form.fields['standing_committees'].choices] + [x for x,y in form.fields['operational_committees'].choices]
                for committee in committee_choices:
                    # if the committee is one that the brother has been assigned to
                    if committee in chosen_committees:
                        # adds the brother to the committee's member list again
                        committee_object = Committee.objects.get(committee=committee)
                        committee_object.members.add(brother)
                        committee_object.save()
                        # if the brother was not previously a part of the committee
                        if committee not in brother_committees:
                            # iterates through all of the committee meetings after now
                            for meeting in committee_object.meetings.exclude(date__lte=datetime.datetime.now(), eligible_attendees=brother):
                                # if the meeting hasn't been previously added to the committee_map, adds it
                                # adds brother: true to the dictionary associated with this meeting
                                if meeting not in meeting_map:
                                    meeting_map[meeting] = {brother: True}
                                # if the meeting has been added, add the brother to the dictionary
                                else:
                                    meeting_map[meeting][brother] = True
                    # if the brother wasn't added to this committee
                    else:
                        # if the the brother was previously part of this commitee
                        if committee in brother_committees:
                            # iterate through all of the committee meetings after now
                            for meeting in Committee.objects.get(committee=committee).meetings.filter(date__gt=datetime.datetime.now(), eligible_attendees=brother):
                                # if the meeting hasn't been previously added to the committee_map, adds it
                                # adds brother: false to the dictionary associated with this meeting
                                if meeting not in meeting_map:
                                    meeting_map[meeting] = {brother: False}
                                else:
                                    meeting_map[meeting][brother] = False
            # for every meeting in the mapping, add the brothers associated with that meeting to the
            # eligible attendees list if true is assigned to the brother, and removes it if false
            for meeting, brother_map in meeting_map.items():
                add_list = [brother_face for brother_face, boo in brother_map.items() if boo is True]
                remove_list = [brother_face for brother_face, boo in brother_map.items() if boo is False]
                meeting.eligible_attendees.add(*add_list)
                meeting.eligible_attendees.remove(*remove_list)
                meeting.attendees_brothers.remove(*remove_list)
                meeting.save()
            return HttpResponseRedirect(reverse('dashboard:committee_list'))
    context = {
        'brother_forms': brother_forms,
    }

    return render(request, 'committee-assignment.html', context)


@verify_position(['vice-president', 'president', 'adviser'])
@transaction.atomic
def in_house(request):
    """Allows the VP to select who's living in the house"""

    form = InHouseForm(request.POST or None)
    position = Position.objects.get(title='vice-president')

    if request.method == 'POST':
        if form.is_valid():
            InHouseForm.brothers.update(in_house=False)
            for c in ['in_house']:
                brothers = form.cleaned_data[c]
                for b in brothers:
                    b.in_house = True
                    b.save()
        return HttpResponseRedirect(reverse('dashboard:vice_president_in_house'))

    context = {
        'form': form,
        'position': position,
    }
    return render(request, 'vice-president/in-house.html', context)
