from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from dashboard.models import Brother, Position, Report
from dashboard.utils import verify_position

@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_agenda(request):
    c_reports = Report.objects.filter(is_officer=False).order_by('brother')
    communications = []
    previous = Brother
    brother = []
    for communication in c_reports:
        if previous == communication.brother:
            brother.append(communication)
        else:
            if brother:
                communications.append(brother)
            brother = [communication]
            previous = communication.brother
    communications.append(brother)

    o_reports = Report.objects.filter(is_officer=True).order_by('position')
    reports = []
    previous = Position
    position = []
    for report in o_reports:
        if previous == report.position:
            position.append(report)
        else:
            if position:
                reports.append(position)
            position = [report]
            previous = report.position
    reports.append(position)

    if request.method == 'POST':
        Report.objects.all().delete()
        return HttpResponseRedirect(reverse('dashboard:secretary_agenda'))

    context = {
        'communications': communications,
        'reports': reports,
    }

    return render(request, 'secretary-agenda.html', context)
