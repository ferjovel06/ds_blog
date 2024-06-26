from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
from ..models import Post

register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def get_latest_posts(count=5):
    return Post.published.order_by('-publish')[:count]


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(texto):
    return mark_safe(markdown.markdown(texto))
