from django.urls import path
from tasks.views import (
    CreateTask,
    ViewProject,
    TaskDetails,
    UpdateTask_Generic,
    DeleteTask,
    EmployeeDashboard,
    ManagerDashboard,
)


urlpatterns = [
    path("manager-dashboard/", ManagerDashboard.as_view(), name="mgr-dashboard"),
    path("user-dashboard/", EmployeeDashboard.as_view(), name="user-dashboard"),
    path("create-task/", CreateTask.as_view(), name="create-task"),
    path("view-task/", ViewProject.as_view(), name="view-task"),
    path("task/<int:task_id>/details/", TaskDetails.as_view(), name="task-details"),
    path("update-task/<int:id>/", UpdateTask_Generic.as_view(), name="update-task"),
    path("delete-task/<int:id>/", DeleteTask.as_view(), name="delete-task"),
]
