from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def modulo(value, arg):
    """Returns the remainder of value divided by arg"""
    return int(value) % int(arg)

@register.filter
def divisibleby(value, arg):
    """Returns the integer division of value by arg"""
    return int(value) // int(arg)

@register.filter
def duration_format(duration):
    """Format a duration into a readable string"""
    if not duration:
        return "--"
    
    total_seconds = int(duration.total_seconds())
    
    # Format as minutes:seconds or hours:minutes:seconds
    if total_seconds < 3600:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes} min {seconds} sec"
    else:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours} hr {minutes} min {seconds} sec"

@register.filter
def percentage(value, max_value):
    try:
        return min(value * 100 / max_value, 100)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    try:
        return value / arg
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def get_avg_score(attempts):
    if not attempts:
        return 0
    
    try:
        total = sum(attempt.score for attempt in attempts)
        return total / len(attempts)
    except Exception:
        return 0

@register.filter
def get_percentage(value, max_value):
    try:
        return (value / max_value) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def time_diff(end_time, start_time):
    try:
        if end_time and start_time:
            return end_time - start_time
        return ""
    except Exception:
        return ""

@register.filter
def format_time(time_value):
    if isinstance(time_value, timedelta):
        # Format timedelta
        seconds = time_value.total_seconds()
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    return time_value 