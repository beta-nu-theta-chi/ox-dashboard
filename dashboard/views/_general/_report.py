from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import render

from dashboard.models import Position, Report
from dashboard.forms import ReportForm
from dashboard.utils import verify_brother

from dashboard.views._dashboard_generic_views import DashboardUpdateView, DashboardDeleteView


def create_report(request):
    brother = request.user.brother
    positions = brother.position_set.exclude(title__in=['Adviser'])

    form = ReportForm(request.POST or None)

    if Position.objects.get(title='Secretary') in positions:
        form.fields["position"].queryset = Position.objects.exclude(title__in=['Adviser'])
    else:
        form.fields["position"].queryset = positions

    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.save()
            if Position.objects.get(title='Secretary') in positions:
                return HttpResponseRedirect(reverse('dashboard:secretary_agenda'))
            else:
                return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'form': form,
        'brother': brother,
        'title': 'Submit Officer Report or Communication'
    }

    return render(request, "model-add.html", context)


class DeleteReport(DashboardDeleteView):
    def get(self, request, *args, **kwargs):
        report = Report.objects.get(pk=self.kwargs['pk'])
        brother = report.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(DeleteReport, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next')

    model = Report
    template_name = 'generic-forms/base-confirm-delete.html'


class EditReport(DashboardUpdateView):
    def get(self, request, *args, **kwargs):
        report = Report.objects.get(pk=self.kwargs['pk'])
        brother = report.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(EditReport, self).get(request, *args, **kwargs)

    def get_form(self):
        form = super().get_form()
        form.fields["position"].queryset = Report.objects.get(pk=self.kwargs['pk']).brother.position_set.exclude(title__in=['Adviser'])
        return form

    model = Report
    template_name = 'generic-forms/base-form.html'
    success_url = reverse_lazy('dashboard:brother')
    fields = ['position', 'information']
