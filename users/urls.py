from django.urls import path
from users.views import (
    CustomLoginView,
    ProfileView,
    ChangePassword,
    CustomPasswordResetView,
    PasswordResetConfirmView,
    SignUp,
    UpdateProfile,
    GroupList,
    CreateGroup,
    AssignRole,
    AdminDashboard,
    ActivateUser,
)
from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeDoneView,
)

urlpatterns = [
    path("sign-up/", SignUp.as_view(), name="sign-up"),
    path("sign-in/", CustomLoginView.as_view(), name="sign-in"),
    path("log-out/", LogoutView.as_view(), name="log-out"),
    path(
        "activate/<int:user_id>/<str:token>/", ActivateUser.as_view(), name="activate"
    ),
    path("admin/dashboard/", AdminDashboard.as_view(), name="admin-dashboard"),
    path("admin/<int:user_id>/assign-role/", AssignRole.as_view(), name="assign-role"),
    path("admin/create-group/", CreateGroup.as_view(), name="create-group"),
    path("admin/groups/", GroupList.as_view(), name="group-list"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("password-change/", ChangePassword.as_view(), name="password-change"),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html",
        ),
        name="password_change_done",
    ),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("edit-profile/", UpdateProfile.as_view(), name="edit-profile"),
]
