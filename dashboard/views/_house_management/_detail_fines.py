from django.contrib.auth.decorators import login_required

from dashboard.views._positions._non_ec._detail_manager import detail_fine_helper

@login_required
def detail_fines(request):
    brother = request.user.brother
    return detail_fine_helper(request, brother)
