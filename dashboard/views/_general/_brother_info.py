from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from  dashboard.models import Brother


def brother_info_list(request):
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))

    """ Renders brother info page """
    brothers = Brother.objects.order_by("brother_status", "last_name", "first_name")
    brother_count = Brother.objects.filter(brother_status="1").count()
    candidate_count = Brother.objects.filter(brother_status="0").count()

    context = {
        'brothers': brothers,
        'brother_count': brother_count,
        'candidate_count': candidate_count,
    }
    return render(request, 'brother-info-list.html', context)
