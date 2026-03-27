from django import template

register = template.Library()

@register.filter(name='reg_index')
def reg_index(indexable, i):
    try:
        return indexable[i]
    except (IndexError, TypeError):
        return None
