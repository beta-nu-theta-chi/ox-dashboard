from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView, DeleteView

from dashboard.models import Excuse
from dashboard.utils import verify_brother

def brother_excuse(request, excuse_id):

    """ Renders the brother page for one of their excuses """
    excuse = Excuse.objects.get(pk=excuse_id)
    if not request.user == excuse.brother.user:  # brother auth check
        messages.error(request, "Please log into the brother that submitted that excuse")
        return HttpResponseRedirect(reverse('dashboard:home'))

    context = {
        'excuse': excuse,
        'type': 'review',
    }
    return render(request, "excuse.html", context)


class ExcuseDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        excuse = Excuse.objects.get(pk=self.kwargs['pk'])
        brother = excuse.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ExcuseDelete, self).get(request, *args, **kwargs)

    model = Excuse
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:brother')


class ExcuseEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        excuse = Excuse.objects.get(pk=self.kwargs['pk'])
        brother = excuse.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ExcuseEdit, self).get(request, *args, **kwargs)

    model = Excuse
    success_url = reverse_lazy('dashboard:brother')
    fields = ['description']
