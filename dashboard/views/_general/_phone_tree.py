from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from dashboard.models import Position
from dashboard.utils import notifies

def emergency_phone_tree_view(request):
    """ Renders the brother page of current user showing all standard brother information """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother needs to be logged in before viewing brother portal")
        return HttpResponseRedirect(reverse('dashboard:home'))

    ec_positions = filter(Position.in_ec, Position.objects.all())

    phone_tree = []
    for position in ec_positions:
        brother = position.brothers.all()[0]
        phone_tree.append({
            'position': position,
            'brother': brother,
            'notifies': notifies(brother)
        })

    context = {
        'phone_tree' : phone_tree
    }

    return render(request, 'general/emergency-phone-tree.html', context)
