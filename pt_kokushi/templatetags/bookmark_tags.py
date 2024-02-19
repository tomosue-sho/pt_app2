from django import template
from pt_kokushi.models import Bookmark

register = template.Library()

@register.filter
def is_bookmarked(question, user):
    return Bookmark.objects.filter(question=question, user=user).exists()
