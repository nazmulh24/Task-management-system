from django.shortcuts import render, redirect, get_object_or_404
from tasks.forms import TaskModelForm, TaskDetailModelForm
from tasks.models import Task, Project
from django.db.models import Q, Count
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
from django.views.generic import ListView, DetailView, UpdateView


def is_manager(user):
    return user.is_authenticated and user.groups.filter(name="Manager").exists()


def is_employee(user):
    return user.is_authenticated and user.groups.filter(name="Employee").exists()


manager_dashboard_decorators = [
    login_required,
    user_passes_test(is_manager, login_url="no-permission"),
]


@method_decorator(manager_dashboard_decorators, name="dispatch")
class ManagerDashboard(View):
    def get(self, request, *args, **kwargs):
        filter_type = request.GET.get("type", "all")

        counts = Task.objects.aggregate(
            total_task=Count("id"),
            completed_task=Count("id", Q(status="COMPLETED")),
            in_progress_task=Count("id", Q(status="IN_PROGRESS")),
            pending_task=Count("id", Q(status="PENDING")),
        )

        base_query = Task.objects.select_related("details").prefetch_related(
            "assigned_to"
        )

        if filter_type == "completed":
            tasks = base_query.filter(status="COMPLETED")
        elif filter_type == "in_progress":
            tasks = base_query.filter(status="IN_PROGRESS")
        elif filter_type == "pending":
            tasks = base_query.filter(status="PENDING")
        else:
            tasks = base_query.all()

        context = {
            "tasks": tasks,
            "counts": counts,
        }
        return render(request, "Dashboard/manager-dashboard.html", context)


employee_dashboard_decorators = [
    login_required,
    user_passes_test(is_employee, login_url="no-permission"),
]


@method_decorator(employee_dashboard_decorators, name="dispatch")
class EmployeeDashboard(View):
    def get(self, request, *args, **kwargs):
        return render(request, "Dashboard/user-dashboard.html")


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
            try:
                task = task_form.save()
                task_detail = task_detail_form.save(commit=False)
                task_detail.task = task
                task_detail.save()

                messages.success(request, "Task added successfully!")
                return redirect(
                    "mgr-dashboard"
                )  # ✅ Use a redirect after successful post

            except Exception as e:
                messages.error(request, f"Error creating task: {e}")

        # If forms are invalid or exception occurs
        context = self.get_context_data(
            task_form=task_form, task_detail_form=task_detail_form
        )
        return render(request, self.template_name, context)


class UpdateTask_Generic(UpdateView):
    model = Task
    form_class = TaskModelForm
    template_name = "task_form.html"
    context_object_name = "task"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["task_form"] = self.get_form()

        if hasattr(self.object, "details") and self.object.details:
            context["task_detail_form"] = TaskDetailModelForm(
                instance=self.object.details
            )
        else:
            context["task_detail_form"] = TaskDetailModelForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        task_form = TaskModelForm(request.POST, instance=self.object)

        task_detail_form = TaskDetailModelForm(
            request.POST, request.FILES, instance=getattr(self.object, "details", None)
        )

        if task_form.is_valid() and task_detail_form.is_valid():
            task = task_form.save()
            task_detail = task_detail_form.save(commit=False)
            task_detail.task = task
            task_detail.save()

            messages.success(request, "Task updated successfully!")
            return redirect("update-task", self.object.id)

        return redirect("update-task", self.object.id)


delete_task_decorator = [
    login_required,
    permission_required("tasks.delete_task", login_url="no-permission"),
]


@method_decorator(delete_task_decorator, name="dispatch")
class DeleteTask(View):
    def post(self, request, id, *args, **kwargs):
        task = get_object_or_404(Task, id=id)
        task.delete()
        messages.success(request, "Task deleted successfully!!")
        return redirect("mgr-dashboard")

    def get(self, request, id, *args, **kwargs):
        messages.error(
            request, "Invalid request method. Please use POST to delete a task."
        )
        return redirect("mgr-dashboard")


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


task_details_decorator = [
    login_required,
    permission_required("tasks.view_task", login_url="no-permission"),
]


@method_decorator(task_details_decorator, name="dispatch")
class TaskDetails(DetailView):
    model = Task
    template_name = "task_details.html"
    context_object_name = "task"
    pk_url_kwarg = "task_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choise"] = Task.STATUS_OPTIONS
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        select_status = request.POST.get("task_status")
        task.status = select_status
        task.save()
        return redirect("task-details", task.id)
