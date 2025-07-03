from django.shortcuts import render


# --This is home view
def homee(request):
    return render(request, "homee.html")


def no_permission(request):
    return render(request, "no_permission.html")
