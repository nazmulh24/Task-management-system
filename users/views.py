from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import Group
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
from django.db.models import Prefetch
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.views.generic import TemplateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import CreateView, FormView
from django.contrib.auth import get_user_model

User = get_user_model()


def is_admin(user):
    return user.groups.filter(name="Admin").exists()


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


class CustomLoginView(LoginView):
    form_class = LoginForm

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        print(next_url)
        return next_url if next_url else super().get_success_url()


class ChangePassword(PasswordChangeView):
    template_name = "accounts/password_change.html"
    form_class = CustomPasswordChangeForm


class ActivateUser(View):
    def get(self, request, user_id, token, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)

            if default_token_generator.check_token(user, token):
                user.is_active = True
                user.save()
                return redirect("sign-in")
            else:
                return HttpResponse("Invalid ID or Token.")

        except User.DoesNotExist:
            return HttpResponse("User not found.")


class AdminDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "admin/dashboard.html"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("no-permission")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        users = User.objects.prefetch_related(
            Prefetch("groups", queryset=Group.objects.all(), to_attr="all_groups")
        ).all()

        for user in users:
            if user.all_groups:
                user.group_name = user.all_groups[0].name
            else:
                user.group_name = "No Group Assigned"

        context["users"] = users
        return context


class AssignRole(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "admin/assign_role.html"
    form_class = AssignRoleForm
    success_url = reverse_lazy("admin-dashboard")

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("no-permission")

    def dispatch(self, request, *args, **kwargs):
        self.user_to_edit = get_object_or_404(User, pk=kwargs["user_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        role = form.cleaned_data.get("role")
        self.user_to_edit.groups.clear()
        self.user_to_edit.groups.add(role)

        messages.success(
            self.request, f"Role '{role}' assigned to {self.user_to_edit.username}."
        )
        return super().form_valid(form)


class CreateGroup(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Group
    form_class = CreateGroupForm
    template_name = "admin/create_group.html"
    success_url = reverse_lazy("create-group")

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("no-permission")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f"Group {form.instance.name} has been created successfully.."
        )
        return response


class GroupList(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Group
    template_name = "admin/group_list.html"
    context_object_name = "groups"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect("no-permission")

    def get_queryset(self):
        return Group.objects.prefetch_related("permissions").all()


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
