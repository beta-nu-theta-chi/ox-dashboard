from django.shortcuts import render

from dashboard.forms import PhotoForm
from dashboard.utils import committee_meeting_panel, photo_form, verify_position

# TODO: why was this previously commented out before i did this refactor?
@verify_position(['Public Relations Chair', 'Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def public_relations_c(request):
    committee_meetings, context = committee_meeting_panel('Public Relations Chair')
    context.update({
        'form': photo_form(PhotoForm, request),
    })

    return render(request, 'public-relations-chair.html', context)
