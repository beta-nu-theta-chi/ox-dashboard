from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from dashboard.forms import CommitteeCreateForm
from dashboard.models import Brother, Committee
from dashboard.utils import create_recurring_meetings

def committee_list(request):
    committees = Committee.objects.all()
    brothers = Brother.objects.order_by('last_name')
    current_brother = request.user.brother
    form = CommitteeCreateForm(request.POST or None)
    form.fields["committee"].choices = [e for e in form.fields["committee"].choices if not Committee.objects.filter(committee=e[0]).exists()]
    form.fields["chair"].choices = [e for e in form.fields["chair"].choices if e[0] not in Committee.objects.values_list('chair', flat=True)]

    if current_brother.position_set.filter(title='Vice President'):
        view_type = 'Vice President'
    else:
        view_type = 'brother'

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            instance = form.cleaned_data
            create_recurring_meetings(instance, instance['committee'])
            return HttpResponseRedirect(reverse('dashboard:committee_list'))

    context = {
        'committees': committees,
        'brothers': brothers,
        'form': form,
        'view_type': view_type
    }

    return render(request, 'general/committee-list.html', context)
