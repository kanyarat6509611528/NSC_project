from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect

from app_users.forms import RegisterForm


# Create your views here.

def register(request: HttpRequest):
    # POST
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
    else:
        form = RegisterForm()

    # GET
    context = {"form": form}
    return render(request, "app_users/register.html", context)

@login_required
def profile(request: HttpRequest):
    return render(request, "app_users/profile.html")

@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'app_general/password_change.html', {'form': form})