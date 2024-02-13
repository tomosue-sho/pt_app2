# your_app/templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter(name='is_bookmarked')
def is_bookmarked(question, user):
    return question.bookmark_set.filter(user=user).exists()
