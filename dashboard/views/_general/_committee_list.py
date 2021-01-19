from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from dashboard.forms import CommitteeCreateForm
from dashboard.models import Brother, Committee, query_positions_with_committee, Position
from dashboard.utils import create_recurring_meetings


def committee_list(request):
    committees = Committee.objects.all()
    brothers = Brother.objects.order_by('last_name')
    current_brother = request.user.brother
    form = CommitteeCreateForm(request.POST or None)
    form.fields["committee"].choices = [e for e in form.fields["committee"].choices if not Committee.objects.filter(committee=e[0]).exists()]

    if current_brother.position_set.filter(title='vice-president'):
        view_type = 'Vice President'
    else:
        view_type = 'brother'

    if request.method == 'POST':
        if form.is_valid():
            committee = form.save(commit=False)
            instance = form.cleaned_data
            index = Committee.CommitteeChoices.values.index(instance['committee'])
            positions = Position.objects.filter(query_positions_with_committee())
            committee.chair = positions[index]
            committee.save()
            create_recurring_meetings(instance, instance['committee'])
            return HttpResponseRedirect(reverse('dashboard:committee_list'))

    context = {
        'committees': committees,
        'brothers': brothers,
        'form': form,
        'view_type': view_type
    }

    return render(request, 'general/committee-list.html', context)
