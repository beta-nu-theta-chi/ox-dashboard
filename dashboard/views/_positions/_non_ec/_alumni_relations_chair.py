from django.shortcuts import render

from dashboard.utils import committee_meeting_panel, verify_position


@verify_position(['alumni-relations-chair', 'vice-president', 'president', 'adviser'])
def alumni_relations_c(request):
    committee_meetings, context = committee_meeting_panel('alumni-relations-chair')

    return render(request, 'alumni-relations-chair.html', context)
