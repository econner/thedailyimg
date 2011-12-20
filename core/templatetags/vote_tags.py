from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
register = template.Library()
from core.models import VoteCount

@register.simple_tag
def vote_count(image, category):
    try:
        vc = VoteCount.objects.get(image=image, category=category)
        return vc.votes
    except VoteCount.DoesNotExist:
        return 0