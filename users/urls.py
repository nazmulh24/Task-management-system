from django.urls import path
from users.views import sign_up, sign_in, log_out

urlpatterns = [
    path("sign-up/", sign_up, name="sign-up"),
    path("sign-in/", sign_in, name="sign-in"),
    path("log-out/", log_out, name="log-out"),
]
