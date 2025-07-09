from django.shortcuts import render, redirect, get_object_or_404
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
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import ContextMixin
from django.views.generic import ListView


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


# @login_required
# @permission_required("tasks.add_task", login_url="no-permission")
# def create_task(request):
#     task_form = TaskModelForm()  # for GET
#     task_detail_form = TaskDetailModelForm()

#     if request.method == "POST":
#         task_form = TaskModelForm(request.POST)
#         task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

#         if task_form.is_valid() and task_detail_form.is_valid():

#             """For Model Form Data"""
#             task = task_form.save()
#             task_detail = task_detail_form.save(commit=False)
#             task_detail.task = task
#             task_detail.save()

#             messages.success(request, "Task added successfully!!")
#             return redirect("create-task")

#     context = {
#         "task_form": task_form,
#         "task_detail_form": task_detail_form,
#     }
#     return render(request, "task_form.html", context)


class CreateTask(ContextMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "tasks.add_task"
    login_url = "sign-in"

    template_name = "task_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_form"] = kwargs.get("task_form", TaskModelForm())
        context["task_detail_form"] = kwargs.get(
            "task_detail_form", TaskDetailModelForm()
        )
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_form = TaskModelForm(request.POST)
        task_detail_form = TaskDetailModelForm(request.POST, request.FILES)

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task added successfully!!")
            context = self.get_context_data(
                task_form=task_form, task_detail_form=task_detail_form
            )
            return render(request, self.template_name, context)


# @login_required
# @permission_required("tasks.change_task", login_url="no-permission")
# def update_task(request, id):
#     task = Task.objects.get(id=id)

#     task_form = TaskModelForm(instance=task)  # for GET
#     task_detail_form = TaskDetailModelForm()

#     if task.details:
#         task_detail_form = TaskDetailModelForm(instance=task.details)

#     if request.method == "POST":
#         task_form = TaskModelForm(request.POST, instance=task)
#         task_detail_form = TaskDetailModelForm(request.POST, instance=task.details)

#         if task_form.is_valid() and task_detail_form.is_valid():

#             """For Model Form Data"""
#             task = task_form.save()
#             task_detail = task_detail_form.save(commit=False)
#             task_detail.task = task
#             task_detail_form.save()

#             messages.success(request, "Task Updated successfully!!")
#             return redirect("update-task", id)

#     context = {
#         "task_form": task_form,
#         "task_detail_form": task_detail_form,
#     }
#     return render(request, "task_form.html", context)


update_decorators = [
    login_required,
    permission_required("tasks.change_task", login_url="no-permission"),
]


@method_decorator(update_decorators, name="dispatch")
class UpdateTask(View):
    template_name = "task_form.html"

    def get(self, request, *args, **kwargs):
        task_id = kwargs.get("id")
        task = get_object_or_404(Task, id=task_id)

        task_form = TaskModelForm(instance=task)
        task_detail_form = TaskDetailModelForm()

        context = {"task_form": task_form, "task_detail_form": task_detail_form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        task_id = kwargs.get("id")
        task = get_object_or_404(Task, id=task_id)
        task_details = getattr(task, "details", None)

        task_form = TaskModelForm(request.POST, instance=task)
        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=task_details
        )

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task updated successfully!")
            return redirect("update-task", id=task.id)


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


view_project_decorator = [
    login_required,
    permission_required("projects.view_project", login_url="no-permission"),
]
@method_decorator(view_project_decorator, name="dispatch")
class ViewProject(ListView):
    model = Project
    context_object_name = "task_cnt"
    template_name = "show_task.html"

    def get_queryset(self):
        queryset = Project.objects.annotate(num_task=Count("task")).order_by("num_task")
        return queryset


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
