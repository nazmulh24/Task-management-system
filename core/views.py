from django.shortcuts import render


def homee(request):
    return render(request, "homee.html")
