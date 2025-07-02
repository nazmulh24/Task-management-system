from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from users.forms import RegisterForm, CustomRegisterForm


def sign_up(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            form.save()

    else:
        form = CustomRegisterForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


def sign_in(request):
    if request.method == "POST":
        # print(request.POST)

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("Home")

    return render(request, "registration/login.html")
