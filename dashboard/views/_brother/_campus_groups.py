from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from dashboard.models import CampusGroup
from dashboard.forms import CampusGroupForm

def campus_groups_add(request):

    brother = request.user.brother

    form = CampusGroupForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            group, created = CampusGroup.objects.get_or_create(name=instance.name)
            group.brothers.add(brother)
            group.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'brother': brother,
        'title': 'Add Your Campus Groups',
        'form': form,
    }

    return render(request, 'model-add.html', context)


def campus_groups_delete(request, pk):
    brother = request.user.brother
    CampusGroup.objects.get(pk=pk).brothers.remove(brother)

    return HttpResponseRedirect(reverse('dashboard:brother'))

