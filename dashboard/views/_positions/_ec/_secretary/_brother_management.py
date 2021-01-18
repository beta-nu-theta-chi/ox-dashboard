from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from dashboard.forms import BrotherForm, BrotherEditForm
from dashboard.models import Brother, User
from dashboard.utils import verify_position

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_list(request):
    """ Renders the Secretary way of viewing brothers """
    brothers = Brother.objects.exclude(brother_status='2')
    context = {
        'position': 'Secretary',
        'brothers': brothers
    }
    return render(request, "secretary/brother-list.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_view(request, brother_id):
    """ Renders the Secretary way of viewing a brother """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother,
        'position': 'Secretary'
    }
    return render(request, "brother-view.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_add(request):
    """ Renders the Secretary way of viewing a brother """
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
            return HttpResponseRedirect(reverse('dashboard:secretary_brother_list'))

    context = {
        'title': 'Add New Brother',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class SecretaryBrotherEdit(DashboardUpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(SecretaryBrotherEdit, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:secretary_brother_list')
    form_class = BrotherEditForm


class SecretaryBrotherDelete(DashboardDeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(SecretaryBrotherDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'generic-forms/base-confirm-delete.html'
    success_url = reverse_lazy('dashboard:secretary')
