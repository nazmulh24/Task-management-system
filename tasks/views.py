from django.shortcuts import render, redirect
from django.http import HttpResponse
from tasks.forms import TaskForm, TaskModelForm, TaskDetailModelForm
from tasks.models import Task, TaskDetail, Project
from datetime import date
from django.db.models import Q, Count, Max, Min, Sum, Avg
from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
    permission_required,
)


def is_manager(user):
    return user.is_authenticated and user.groups.filter(name="Manager").exists()


def is_employee(user):
    return user.is_authenticated and user.groups.filter(name="Employee").exists()


@user_passes_test(is_manager, login_url="no-permission")
def manager_dashboard(request):

    type = request.GET.get("type", "all")
    # print(type)

    counts = Task.objects.aggregate(
        total_task=Count("id"),
        completed_task=Count("id", Q(status="COMPLETED")),
        in_progress_task=Count("id", Q(status="IN_PROGRESS")),
        pending_task=Count("id", Q(status="PENDING")),
    )

    base_query = Task.objects.select_related("details").prefetch_related("assigned_to")

    if type == "completed":
        tasks = base_query.filter(status="COMPLETED")
    elif type == "in_progress":
        tasks = base_query.filter(status="IN_PROGRESS")
    elif type == "pending":
        tasks = base_query.filter(status="PENDING")
    elif type == "all":
        tasks = base_query.all()

    context = {
        "tasks": tasks,
        "counts": counts,
    }
    return render(request, "Dashboard/manager-dashboard.html", context)


@user_passes_test(is_employee, login_url="no-permission")
def employee_dashboard(request):
    return render(request, "Dashboard/user-dashboard.html")


@login_required
@permission_required("tasks.add_task", login_url="no-permission")
def create_task(request):
    task_form = TaskModelForm()  # for GET
    task_detail_form = TaskDetailModelForm()

    if request.method == "POST":
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():

            """For Model Form Data"""
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task added successfully!!")
            return redirect("create-task")

    context = {
        "task_form": task_form,
        "task_detail_form": task_detail_form,
    }
    return render(request, "task_form.html", context)


@login_required
@permission_required("tasks.change_task", login_url="no-permission")
def update_task(request, id):
    task = Task.objects.get(id=id)

    task_form = TaskModelForm(instance=task)  # for GET
    task_detail_form = TaskDetailModelForm()

    if task.details:
        task_detail_form = TaskDetailModelForm(instance=task.details)

    if request.method == "POST":
        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(request.POST, instance=task.details)

        if task_form.is_valid() and task_detail_form.is_valid():

            """For Model Form Data"""
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail_form.save()

            messages.success(request, "Task Updated successfully!!")
            return redirect("update-task", id)

    context = {
        "task_form": task_form,
        "task_detail_form": task_detail_form,
    }
    return render(request, "task_form.html", context)


@login_required
@permission_required("tasks.delete_task", login_url="no-permission")
def delete_task(request, id):
    if request.method == "POST":
        task = Task.objects.get(id=id)
        task.delete()
        messages.success(request, "Task deleted successfully!!")
        return redirect("mgr-dashboard")
    else:
        messages.error(
            request, "Invalid request method. Please use POST to delete a task."
        )
        return redirect("mgr-dashboard")


@login_required
@permission_required("tasks.view_task", login_url="no-permission")
def view_task(request):
    task_cnt = Project.objects.annotate(num_task=Count("task")).order_by("num_task")

    return render(request, "show_task.html", {"task_cnt": task_cnt})


@login_required
@permission_required("tasks.view_task", login_url="no-permission")
def task_details(request, task_id):
    task = Task.objects.get(id=task_id)
    status_choise = Task.STATUS_OPTIONS
    if request.method == "POST":
        select_status = request.POST.get("task_status")
        task.status = select_status
        task.save()

        return redirect("task-details", task.id)

    return render(
        request,
        "task_details.html",
        {
            "task": task,
            "status_choise": status_choise,
        },
    )
