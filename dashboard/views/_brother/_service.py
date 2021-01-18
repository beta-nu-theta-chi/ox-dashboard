from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from dashboard.forms import ServiceSubmissionForm
from dashboard.models import ServiceSubmission
from dashboard.utils import verify_brother, get_semester

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


def brother_service_submission(request, submission_id):
    """ Renders the Brother page for viewing a service submission"""
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before adding service hours")
        return HttpResponseRedirect(reverse('dashboard:home'))

    submission = ServiceSubmission.objects.get(pk=submission_id)

    context = {
        'type': 'review',
        'submission': submission,
    }

    return render(request, 'service-chair/service-submission.html', context)


def brother_service_submission_add(request):
    """ Renders the Brother page for adding a service submission"""
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before adding service hours")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = ServiceSubmissionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            semester = get_semester()
            brother = request.user.brother
            instance.brother = brother
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'title': 'Submit Service Hours',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class ServiceSubmissionDelete(DashboardDeleteView):
    def get(self, request, *args, **kwargs):
        submission = ServiceSubmission.objects.get(pk=self.kwargs['pk'])
        brother = submission.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceSubmissionDelete, self).get(request, *args, **kwargs)

    template_name = 'generic-forms/base-confirm-delete.html'
    model = ServiceSubmission
    success_url = reverse_lazy('dashboard:brother')


class ServiceSubmissionEdit(DashboardUpdateView):
    def get(self, request, *args, **kwargs):
        submission = ServiceSubmission.objects.get(pk=self.kwargs['pk'])
        brother = submission.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceSubmissionEdit, self).get(request, *args, **kwargs)

    model = ServiceSubmission
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:brother')
    form_class = ServiceSubmissionForm

