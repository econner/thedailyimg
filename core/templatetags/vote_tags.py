from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
register = template.Library()
from core.models import VoteCount, Vote

@register.simple_tag
def vote_count(image, category):
    return VoteCount.get_vote_count(image_id=image, cat_id=category)
        
@register.simple_tag(takes_context=True)
def user_has_voted(context, image, category, score):
    if not context['user'].is_authenticated():
        return ""
    
    return Vote.check_user_vote_type(user=context['user'], image=image, category=category, score=int(score))