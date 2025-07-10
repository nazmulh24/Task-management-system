from django import template
from datetime import datetime, timedelta
from django.utils import timezone

register = template.Library()


@register.filter
def humanized_date(value):
    if value:
        value = timezone.localtime(value)
        today = datetime.now().date()
        # today = timezone.localtime().date()
        yesterday = today - timedelta(days=1)

        if value.date() == today:
            return f"Today at {value.strftime('%I:%M %p')}"
        elif value.date() == yesterday:
            return f"Yesterday at {value.strftime('%I:%M %p')}"
        else:
            return value.strftime("%B %d, %Y at %I:%M %p")

    return "No Login Record Available"
