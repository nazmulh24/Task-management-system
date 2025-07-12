from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import  Group
from django.contrib.auth import authenticate, login, logout
from users.forms import (
    CustomRegisterForm,
    LoginForm,
    AssignRoleForm,
    CreateGroupForm,
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomConfirmPasswordForm,
    EditProfileForm,
)
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import get_user_model

User = get_user_model()


"""
class UpdateProfile(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "accounts/update_profile.html"
    context_object_name = "form"

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["userprofile"] = UserProfile.objects.get(user=self.request.user)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfile.objects.get(user=self.request.user)
        context["form"] = self.form_class(
            instance=self.get_object(), userprofile=user_profile
        )
        return context

    def form_valid(self, form):
        form.save(commit=True)
        return redirect("profile")
"""


class UpdateProfile(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "accounts/update_profile.html"
    context_object_name = "form"

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        form.save()
        return redirect("profile")


def is_admin(user):
    return user.groups.filter(name="Admin").exists()


def sign_up(request):
    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("pass1"))
            user.is_active = False
            user.save()
            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return redirect("sign-in")

    else:
        form = CustomRegisterForm()

    context = {"form": form}
    return render(request, "registration/register.html", context)


class SignUp(View):
    template_name = "registration/register.html"
    form_class = CustomRegisterForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get("pass1"))
            user.is_active = False
            user.save()

            messages.success(
                request,
                "Registration successful! Please check your email to activate your account.",
            )
            return redirect("sign-in")

        return render(request, self.template_name, {"form": form})


def sign_in(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("Home")

    context = {
        "form": form,
    }
    return render(request, "registration/login.html", context)


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.POST.get("next")  # --------> Problem Here...
        print(next_url)
        return next_url if next_url else super().get_success_url()


class ChangePassword(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = CustomPasswordChangeForm


@login_required
def log_out(request):
    if request.method == "POST":
        logout(request)
        return redirect("Home")


def activate_user(request, user_id, token):
    try:
        user = User.objects.get(id=user_id)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()

            return redirect("sign-in")
        else:
            return HttpResponse("Invalid ID / Token...")

    except User.DoesNotExist:
        return HttpResponse("User Not Found")


@user_passes_test(is_admin, login_url="no-permission")
def admin_dashboard(request):
    users = User.objects.prefetch_related(
        Prefetch("groups", queryset=Group.objects.all(), to_attr="all_groups")
    ).all()

    for user in users:
        if user.all_groups:
            user.group_name = user.all_groups[0].name
        else:
            user.group_name = "No Group Assigned"

    context = {
        "users": users,
    }
    return render(request, "admin/dashboard.html", context)


@user_passes_test(is_admin, login_url="no-permission")
def assign_role(request, user_id):
    user = User.objects.get(id=user_id)
    form = AssignRoleForm()

    if request.method == "POST":
        form = AssignRoleForm(request.POST)

        if form.is_valid():
            role = form.cleaned_data.get("role")
            user.groups.clear()  # --> Remove old roles
            user.groups.add(role)
            messages.success(request, f"Role '{role}' assigned to {user.username}.")

            return redirect("admin-dashboard")

    context = {
        "form": form,
    }
    return render(request, "admin/assign_role.html", context)


@user_passes_test(is_admin, login_url="no-permission")
def create_group(request):
    form = CreateGroupForm()

    if request.method == "POST":
        form = CreateGroupForm(request.POST)

        if form.is_valid():
            group = form.save()
            messages.success(
                request, f"Group {group.name} has been created successfully.."
            )

            return redirect("create-group")

    return render(request, "admin/create_group.html", {"form": form})


@user_passes_test(is_admin, login_url="no-permission")
def group_list(request):
    groups = Group.objects.prefetch_related("permissions").all()

    return render(request, "admin/group_list.html", {"groups": groups})


class ProfileView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["username"] = user.username
        context["email"] = user.email
        context["name"] = user.get_full_name()
        context["bio"] = user.bio
        context["profile_img"] = user.profile_img
        
        context["member_since"] = user.date_joined
        context["last_login"] = user.last_login

        return context


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "registration/reset_password.html"
    success_url = reverse_lazy("sign-in")
    html_email_template_name = "registration/reset_email.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["protocol"] = "https" if self.request.is_secure() else "http"
        context["domain"] = self.request.get_host()

        return context

    def form_valid(self, form):
        messages.success(self.request, "A reset email send. Please check your email...")
        return super().form_valid(form)


class PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomConfirmPasswordForm
    template_name = "registration/reset_password.html"
    success_url = reverse_lazy("sign-in")

    def form_valid(self, form):
        messages.success(self.request, "Password has been reset successfully...")
        return super().form_valid(form)
