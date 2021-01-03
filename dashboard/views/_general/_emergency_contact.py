from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from  dashboard.models import Brother

@login_required
def emergency_contact_list(request):
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))

    """ Renders emergency contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'emergency-contact-list.html', context)
