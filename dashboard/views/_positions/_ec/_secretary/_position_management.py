from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from dashboard.forms import PositionForm
from dashboard.models import Position
from dashboard.utils import verify_position

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def secretary_positions(request):
    """ Renders all of the positions currently in the chapter """
    # Checking to make sure all of the EC and dashboard required positions are setup
    if request.method == 'POST':
        for position in Position.PositionChoices.values:
            if not Position.objects.filter(title=position).exists():
                new_position = Position(title=position)
                new_position.save()
        return HttpResponseRedirect(reverse('dashboard:secretary_positions'))

    # doing a .all() ensures that the positions are listed in order of succession since they're created in that order
    positions = Position.objects.all()
    context = {
        'positions': positions,
    }
    return render(request, "secretary/positions.html", context)


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def secretary_position_add(request):
    """ Renders the Secretary way of viewing a brother """
    form = PositionForm(request.POST or None)
    form.fields["title"].choices = [e for e in form.fields["title"].choices if not Position.objects.filter(title=e[0]).exists()]

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:secretary_positions'))

    context = {
        'title': 'Add New Position',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class PositionEdit(DashboardUpdateView):
    @verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
    def get(self, request, *args, **kwargs):
        return super(PositionEdit, self).get(request, *args, **kwargs)

    model = Position
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:secretary_positions')
    fields = ['brothers']


class PositionDelete(DashboardDeleteView):
    @verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
    def get(self, request, *args, **kwargs):
        return super(PositionDelete, self).get(request, *args, **kwargs)

    model = Position
    template_name = 'generic-forms/base-confirm-delete.html'
    success_url = reverse_lazy('dashboard:secretary_positions')
