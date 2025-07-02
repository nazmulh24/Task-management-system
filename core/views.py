from django.shortcuts import render


# --This is home view
def homee(request):
    return render(request, "homee.html")
