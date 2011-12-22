from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
register = template.Library()
from core.models import VoteCount, Vote

@register.simple_tag
def vote_count(image, category):
    try:
        vc = VoteCount.objects.get(image=image, category=category)
        return vc.votes
    except VoteCount.DoesNotExist:
        return 0
        
@register.simple_tag(takes_context=True)
def user_has_voted(context, image, category, score):
    if not context['user'].is_authenticated():
        return ""
    
    try:
        v = Vote.objects.get(user=context['user'], votecount__image=image, votecount__category=category)
        if v.score == int(score):
            return "voted"
    except Vote.DoesNotExist:
        pass
    return ""