from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def humanized_date(value):
    if value:
        today = timezone.localtime(timezone.now()).date()
        value = timezone.localtime(value)
        yesterday = today - timedelta(days=1) 
        if value.date() == today:
            return f"Today at {value.strftime('%I:%M %p')}"
        elif value.date() == yesterday:
            return f"Yesterday at {value.strftime('%I:%M %p')}"
        else:
            return value.strftime('%b %d, %Y at %I:%M %p')
    
    return "No login record available!"
