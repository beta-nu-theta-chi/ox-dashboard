from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import DeleteView

from dashboard.models import MediaAccount, OnlineMedia
from dashboard.forms import MediaAccountForm, MediaForm

def media_account_add(request):

    brother = request.user.brother
    form = MediaAccountForm(request.POST or None)

    form.fields["media"].queryset = OnlineMedia.objects.exclude(name__in=[e.media.name for e in brother.media_accounts.all()])
    #list(map(lambda account: account.media.name, brother.media_accounts.all()))
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'brother': request.user.brother,
        'title': 'Media Account',
        'form': form,
        'list': brother.media_accounts.all()
    }

    return render(request, 'brother-info-add.html', context)


class MediaAccountDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        return super(MediaAccountDelete, self).get(request, *args, **kwargs)

    model = MediaAccount
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:brother')


def media_add(request):

    form = MediaForm(request.POST or None)

    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:media_account_add'))

    context = {
        'title': 'Media',
        'form': form
    }

    return render(request, 'model-add.html', context)
