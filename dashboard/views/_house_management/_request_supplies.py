from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from dashboard.forms import SuppliesForm


def supplies_request(request):
    form = SuppliesForm(request.POST or None)
    context = {}

    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=True)
            context['message'] = 'Thanks!'

    context = {
        'form': form,
        'button': 'Request',
    }
    return render(request, 'house-management/request-supplies.html', context)
