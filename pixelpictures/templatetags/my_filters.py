from django import template

register = template.Library()

@register.filter(name='times')
def times(number):
    return range(1, number + 1)

@register.filter(name='timestamp')
def timestamp(time):
    return time.strftime('%Y%m%d_%H%M%S')