# encoding: utf-8
from django.utils.translation import gettext_lazy as _
from django import template
from django.utils.html import format_html


register = template.Library()


@register.simple_tag
def math_sub(value, arg):
    return value - arg


@register.simple_tag
def math_add(value, arg):
    return value + arg


@register.simple_tag
def math_mul(value, arg):
    return value * arg


@register.simple_tag
def math_div(value, arg):
    return value / arg


@register.simple_tag
def to_html(html_str):
    try:
        return format_html(html_str)
    except:
        return ''


@register.filter
def is_not_none(val):
    return val is not None


@register.filter
def yes_no(value):
    return _('Yes') if value is True else _('No')


@register.filter
def from_dict(dictionary, key):
    return dictionary.get(key)


@register.filter
def from_list(lst, key):
    try:
        return lst[key]
    except:
        return ''


@register.filter
def from_choices(dictionary, key):
    for k, v in dictionary:
        if k == key:
            return v
    return ''


@register.filter
def nope(value):
    try:
        return not int(value)
    except:
        return False

@register.inclusion_tag('include/pagination.html', takes_context=True)
def end_pagination(context, page, begin_pages=2, end_pages=2, before_current_pages=4, after_current_pages=4):
    """
    return google like pagination
    Usage::
        {% load end_tags %}
        {% end_pagination the_obj_to_paginate %}

    Example::
        {% end_pagination page_obj %}
    At this case page_obj is the defaul
    object for pages that django provide
    """

    def collides(firstlist, secondlist):
        """
        Returns true if lists collides (have same entries)
        Example::
        >>> collides([1,2,3,4],[3,4,5,6,7])
        True
        >>> collides([1,2,3,4],[5,6,7])
        False
        """
        return any(item in secondlist for item in firstlist)

    before = max(page.number - before_current_pages - 1, 0)
    after = page.number + after_current_pages

    begin = page.paginator.page_range[:begin_pages]
    middle = page.paginator.page_range[before:after]
    end = page.paginator.page_range[-end_pages:]
    last_page_number = end[-1]

    # If middle and end has same entries, then end is what we want
    if collides(middle, end):
        end = range(max(last_page_number - before_current_pages - after_current_pages, 1), last_page_number + 1)  # noqa
        middle = []

    # If begin and middle ranges has same entries, then begin is what we want
    if collides(begin, middle):
        begin = range(1, min(before_current_pages + after_current_pages, last_page_number) + 1)  # noqa
        middle = []

    # If begin and end has the same entries then begin is what we want
    if collides(begin, end):
        begin = range(1, last_page_number + 1)
        end = []

    request = context['request']
    query_filter = ["&%s=%s" % (k, v) for k, v in request.GET.items() if
                    k not in ['page', 'csrfmiddlewaretoken'] and not k.endswith('_checked')]
    return {
        'page': page,
        'begin': begin,
        'middle': middle,
        'end': end,
        'query_filter': ''.join(query_filter),
    }
