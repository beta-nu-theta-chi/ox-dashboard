from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify

from dashboard.forms import ExcuseResponseForm
from dashboard.models import Excuse, RecruitmentEvent, Position
from dashboard.utils import verify_position


@verify_position([Position.PositionChoices.RECRUITMENT_CHAIR, Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def excuse(request, position_slug, excuse_id):
    """ Renders Excuse response form """
    # since this view can be accessed from multiple different pages,in order to redirect back to those pages,
    # pass in a slug for the position doing a redirect on the slug should redirect back to the position's page
    excuse = get_object_or_404(Excuse, pk=excuse_id)
    form = ExcuseResponseForm(request.POST or None, excuse=excuse)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            excuse.status = instance.status
            excuse.response_message = instance.response_message
            excuse.save()
            return HttpResponseRedirect('/' + position_slug)

    context = {
        'type': 'response',
        'excuse': excuse,
        'form': form,
    }
    return render(request, "excuse.html", context)


# accepts the excuse then immediately redirects you back to where you came from
def excuse_quick_accept(request, position_slug, excuse_id):
    # since this view can be accessed from multiple different pages,in order to redirect back to those pages,
    # pass in a slug for the position doing a redirect on the slug should redirect back to the position's page
    excuse = Excuse.objects.get(pk=excuse_id)
    excuse.status = '1'
    excuse.save()
    return HttpResponseRedirect('/' + position_slug)


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def secretary_all_excuses(request):
    """ Renders Excuse archive """
    excuses = Excuse.objects.exclude(status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by('brother__last_name', 'event__date')

    context = {
        'excuses': excuses,
        'position': Position.objects.get(title=Position.PositionChoices.SECRETARY),
    }
    return render(request, 'excuses-archive.html', context)
