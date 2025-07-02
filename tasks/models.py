from django.db import models
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail


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


# -----------------------------> Signals --------- Below

# --> post_save
# @receiver(post_save, sender=Task)
# def notify_task_creation(sender, instance, created, **kwargs):
#     print("sender", sender)
#     print("instance", instance)
#     print("kwargs", kwargs)
#     print("created", created)

#     if created:
#         instance.is_completed = True
#         instance.save()


# --> pre_save
# @receiver(pre_save, sender=Task)
# def notify_task_creation(sender, instance, **kwargs):
#     print("sender", sender)
#     print("instance", instance)
#     print("kwargs", kwargs)

#     instance.is_completed = True


# -----> Sending Email
@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_employees_on_task_creation(sender, instance, action, **kwargs):
    if action == "post_add":
        assigned_emails = [emp.email for emp in instance.assigned_to.all()]

        send_mail(
            "New Task Assigned",
            f"You have been assigned a new task : {instance.title}",
            "snazmulhossains24@gmail.com",
            assigned_emails,
            fail_silently=False,
        )
