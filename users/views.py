from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from users.forms import CustomRegisterForm, LoginForm, AssignRoleForm, CreateGroupForm
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Prefetch


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


@login_required
def log_out(request):
    if request.method == "POST":
        logout(request)
        return redirect("sign-in")


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
