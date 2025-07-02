from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm


def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # return render(request, "registration/register.html")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)
