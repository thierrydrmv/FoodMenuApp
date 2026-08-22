from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        username = form.cleaned_data.get("username")
        messages.success(
            request, f"Welcome {username}, your account have been successfully created."
        )
        return redirect("login")
    context = {"form": form}
    return render(request, "users/register.html", context)


def logout_view(request):
    logout(request)
    return render(request, "users/logout.html")
