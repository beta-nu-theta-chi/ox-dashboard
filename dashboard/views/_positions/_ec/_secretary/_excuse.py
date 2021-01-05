from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify

from dashboard.forms import ExcuseResponseForm
from dashboard.models import Excuse, RecruitmentEvent
from dashboard.utils import verify_position


@verify_position(['Recruitment Chair', 'Secretary', 'Vice President', 'President', 'Adviser'])
def excuse(request, position, excuse_id):
    """ Renders Excuse response form """
    excuse = get_object_or_404(Excuse, pk=excuse_id)
    form = ExcuseResponseForm(request.POST or None, excuse=excuse)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            excuse.status = instance.status
            excuse.response_message = instance.response_message
            excuse.save()
            return HttpResponseRedirect('/' + position)

    context = {
        'type': 'response',
        'excuse': excuse,
        'form': form,
    }
    return render(request, "excuse.html", context)


# accepts the excuse then immediately redirects you back to where you came from
def excuse_quick_accept(request, position, excuse_id):
    excuse = Excuse.objects.get(pk=excuse_id)
    excuse.status = '1'
    excuse.save()
    return HttpResponseRedirect('/' + position)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_excuses(request):
    """ Renders Excuse archive """
    excuses = Excuse.objects.exclude(status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by('brother__last_name', 'event__date')

    context = {
        'excuses': excuses,
        'position': 'Secretary',
    }
    return render(request, 'excuses-archive.html', context)
