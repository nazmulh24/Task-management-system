from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail, EmailMultiAlternatives

from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def send_activation_mail(sender, instance, created, **kwargs):
    if created and instance.email:
        token = default_token_generator.make_token(instance)
        activation_url = (
            f"{settings.FRONTEND_URL}/users/activate/{instance.pk}/{token}/"
        )

        subject = "Activate Your Account"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]

        # ----> Render HTML message
        html_message = render_to_string(
            "registration/activate_email.html",
            {
                "username": instance.username,
                "first_name": instance.first_name,
                "last_name": instance.last_name,
                "activation_url": activation_url,
            },
        )

        # ---> Fallback plain text version
        text_message = strip_tags(html_message)

        try:
            email = EmailMultiAlternatives(
                subject, text_message, from_email, recipient_list
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        except Exception as e:
            print(f"Error sending activation email to {recipient_list} : {str(e)}")


@receiver(post_save, sender=User)
def assign_role(sender, instance, created, **kwargs):
    if created:
        user_group, created = Group.objects.get_or_create(name="User")
        instance.groups.add(user_group)
        instance.save()
