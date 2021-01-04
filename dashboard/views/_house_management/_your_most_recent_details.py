from django.contrib.auth.decorators import login_required

from dashboard.views._positions._non_ec._detail_manager import current_details_helper

@login_required
def current_details(request):
    brother = request.user.brother
    return current_details_helper(request, brother)
