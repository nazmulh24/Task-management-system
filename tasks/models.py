from django.db import models


class Task(models.Model):
    STATUS_OPTIONS = (
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In progress"),
        ("COMPLETED", "Completed"),
    )
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        default=1,
    )
    assigned_to = models.ManyToManyField("Employee")
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_OPTIONS, default="PENDING")
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TaskDetail(models.Model):
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"
    PRIORITY_OPTIONS = (
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    )
    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name="details",
    )
    # assigned_to = models.CharField(max_length=100)
    priority = models.CharField(max_length=1, choices=PRIORITY_OPTIONS, default=LOW)
    notes = models.TextField(blank=True, null=True)  # --> Optional Field

    def __str__(self):
        return f"Details form Task {self.task.title}"


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)  # --> Optional Field
    start_date = models.DateField()

    def __str__(self):
        return self.name


class Employee(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=254)

    def __str__(self):
        return self.name
