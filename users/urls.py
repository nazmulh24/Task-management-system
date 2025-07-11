from django.urls import path
from users.views import (
    sign_up,
    sign_in,
    log_out,
    activate_user,
    admin_dashboard,
    assign_role,
    create_group,
    group_list,
    CustomLoginView,
    ProfileView,
    ChangePassword,
    CustomPasswordResetView,
)
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)

urlpatterns = [
    path("sign-up/", sign_up, name="sign-up"),
    # path("sign-in/", sign_in, name="sign-in"),
    path(
        "sign-in/",
        CustomLoginView.as_view(
            # template_name="registration/login.html",
        ),
        name="sign-in",
    ),
    # path("log-out/", log_out, name="log-out"),
    path("log-out/", LogoutView.as_view(), name="log-out"),
    path("activate/<int:user_id>/<str:token>/", activate_user, name="activate"),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
    path("admin/<int:user_id>/assign-role/", assign_role, name="assign-role"),
    path("admin/create-group/", create_group, name="create-group"),
    path("admin/group-list/", group_list, name="group-list"),
    path("profile/", ProfileView.as_view(), name="profile"),
    # path(
    #     "password-change/",
    #     PasswordChangeView.as_view(
    #         template_name="accounts/password_change.html",
    #     ),
    #     name="password-change",
    # ),
    path("password-change/", ChangePassword.as_view(), name="password-change"),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password-reset"),
]
