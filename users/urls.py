from django.urls import path
from users.views import sign_up, sign_in, log_out, activate_user, admin_dashboard

urlpatterns = [
    path("sign-up/", sign_up, name="sign-up"),
    path("sign-in/", sign_in, name="sign-in"),
    path("log-out/", log_out, name="log-out"),
    path("activate/<int:user_id>/<str:token>/", activate_user, name="activate"),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
]
