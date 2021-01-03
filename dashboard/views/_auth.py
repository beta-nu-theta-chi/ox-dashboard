from django.contrib import auth, messages
from django.urls import reverse
from django.http import HttpResponseRedirect

from dashboard.forms import ChangePasswordForm

class LoginView(View):
    """ Logs in and redirects to the homepage """
    def post(self, request, *args, **kwargs):
        user = auth.authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            if user.is_active:
                auth.login(request, user)
        return HttpResponseRedirect(reverse('dashboard:home'))

    def get(self, request, *args, **kwargs):
        # we should never get to this code path
        return HttpResponseRedirect(reverse('dashboard:home'))


class LogoutView(View):
    """ Logout and redirect to homepage """

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return HttpResponseRedirect(reverse('dashboard:home'))

def change_password(request):
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Cannot change password if you are not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))
    brother = request.user.brother
    form = ChangePasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            user = auth.authenticate(
                username=request.user.username,
                password=instance['old_password']
            )
            if user is not None:
                if instance['new_password'] == instance['retype_new_password']:
                    if instance['new_password'] == instance['old_password']:
                        messages.error(request, "Old password and new password cannot match")
                        return HttpResponseRedirect(reverse('dashboard:change_password'))
                    else:
                        user.set_password(instance['new_password'])
                        user.save()
                        user = auth.authenticate(
                            username=request.user.username,
                            password=instance['new_password']
                        )
                        auth.login(request, user)
                        return HttpResponseRedirect(reverse('dashboard:brother'))
                else:
                    messages.error(request, "New password did not match")
                    return HttpResponseRedirect(reverse('dashboard:change_password'))

    context = {
        'brother': brother,
        'form': form,
    }

    return render(request, "change-password.html", context)
