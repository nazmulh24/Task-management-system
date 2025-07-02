from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.forms import RegisterForm


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
        #     username = form.cleaned_data.get("username")
        #     pass1 = form.cleaned_data.get("password1")
        #     pass2 = form.cleaned_date.get("password2")

        #     if pass1 == pass2:
        #         User.objects.create(username=username, password=pass1)
        #     else:
        #         print("Password are not same")
        # else:
        #     print("Form is not valid...")

    else:
        form = RegisterForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)
