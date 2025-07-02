from django.db.models.signals import post_save, pre_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail

from tasks.models import Task


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


# --> post_delete
@receiver(post_delete, sender=Task)
def delete_associated_detail(sender, instance, **kwargs):
    if instance.details:
        instance.details.delete()
        print(f"Details for task '{instance.title}' have been deleted.")

