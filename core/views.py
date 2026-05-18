from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm
from .models import Profile


class UserLoginView(LoginView):
    authentication_form = LoginForm
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse('agenda_list')


@login_required
def dashboard(request):
    return redirect('agenda_list')


@login_required
def editor_dashboard(request):
    return render(request, 'core/editor_dashboard.html')


@login_required
def lector_dashboard(request):
    return render(request, 'core/lector_dashboard.html')
