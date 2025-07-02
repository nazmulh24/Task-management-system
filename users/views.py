from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from users.forms import RegisterForm, CustomRegisterForm, LoginForm
from django.contrib import messages


def sign_up(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("pass1"))
            user.is_active = False
            user.save()
            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return redirect("sign-in")

    else:
        form = CustomRegisterForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


def sign_in(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("Home")

    context = {
        "form": form,
    }
    return render(request, "registration/login.html", context)


def log_out(request):
    if request.method == "POST":
        logout(request)
        return redirect("sign-in")
