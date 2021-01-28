from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy

from dashboard.forms import BrotherForm, BrotherEditForm
from dashboard.models import Position, Brother
from dashboard.utils import verify_position
from dashboard.views import DashboardUpdateView, DashboardDeleteView


@verify_position([Position.PositionChoices.SECRETARY, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def brother_add(request, position_slug):
    """ Renders the view to add a brother """
    form = BrotherForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.clean()
            user = User.objects.create_user(instance['case_ID'], instance['case_ID'] + "@case.edu",
                                            instance['password'])
            user.last_name = instance['last_name']
            user.save()

            brother = form.save(commit=False)
            brother.user = user
            brother.save()
            return HttpResponseRedirect('/' + position_slug)

    context = {
        'title': 'Add New Brother',
        'form': form,
    }
    return render(request, 'model-add.html', context)


@verify_position([Position.PositionChoices.MARSHAL, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
def ec_brother_view(request, position_slug, brother_id):
    """ Renders the marshal page to view candidate info """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother,
        'position': position_slug,
    }
    return render(request, "brother-view.html", context)


class ECBrotherEdit(DashboardUpdateView):
    @verify_position([Position.PositionChoices.MARSHAL, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
    def get(self, request, *args, **kwargs):
        return super(ECBrotherEdit, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return '/' + self.kwargs['position_slug']

    model = Brother
    template_name = 'generic-forms/base-form.html'
    form_class = BrotherEditForm


class BrotherDelete(DashboardDeleteView):
    @verify_position([Position.PositionChoices.MARSHAL, Position.PositionChoices.VICE_PRESIDENT, Position.PositionChoices.PRESIDENT, Position.PositionChoices.ADVISER])
    def get(self, request, *args, **kwargs):
        return super(BrotherDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return '/' + self.kwargs['position_slug']

    model = Brother
    template_name = 'generic-forms/base-confirm-delete.html'
