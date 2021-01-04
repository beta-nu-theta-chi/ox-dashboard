from django.shortcuts import render

from dashboard.utils import committee_meeting_panel, verify_position

@verify_position(['Alumni Relations Chair', 'Vice President', 'President', 'Adviser'])
def alumni_relations_c(request):
    committee_meetings, context = committee_meeting_panel('Alumni Relations Chair')

    return render(request, 'alumni-relations-chair.html', context)
