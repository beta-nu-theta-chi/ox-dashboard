from django.contrib.auth.decorators import login_required

from dashboard.views._positions._non_ec._detail_manager import all_details_helper

@login_required
def all_details(request):
    brother = request.user.brother
    return all_details_helper(request, brother)
