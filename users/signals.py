from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings


@receiver(post_save, sender=User)
def send_activation_mail(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = (
            f"{settings.FRONTEND_URL}/users/activate/{instance.pk}/{token}/"
        )

        subject = "Activate Your Account"
        message = f"Hi {instance.username},\n\nPlease click the link below to activate your account:\n{activation_url}\n\nThank you!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f"Error sending activation email to {recipient_list} : {str(e)}")
