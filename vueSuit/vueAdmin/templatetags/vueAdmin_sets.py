#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-08-04 00:29
# @Author : ryuchen
# @File : vuetags.py
# @Desc :
# ==================================================
import os
import json
import datetime

from django import template
from django.conf import settings
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import label_for_field, lookup_field, display_for_value, display_for_field
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from django.urls import NoReverseMatch
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.admin.views.main import (
    ALL_VAR, ORDER_VAR, PAGE_VAR, SEARCH_VAR,
)
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from ..settings import VueAdminSettings

vsettings = VueAdminSettings()
register = template.Library()


def unicode_to_str(u):
    return u.encode()


def _field_display(model, field_name):
    for f in model._meta.fields:
        if f.name == field_name:
            if hasattr(f, 'verbose_name'):
                return getattr(f, 'verbose_name')

    return field_name


def __get_config(name):
    value = os.environ.get(name, getattr(settings, name, None))
    return value


def _import_reload(_modules):
    _obj = __import__(_modules, fromlist=_modules.split('.'))
    return _obj


class LazyEncoder(DjangoJSONEncoder):
    """
    解决json __proxy__ 问题
    """

    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


@register.simple_tag
def vue_logo():
    logo = {
        "full": {
            "src": vsettings.get_config('VUEADMIN_HEADER_LOGOFULL')
        },
        "mini": {
            "src": vsettings.get_config('VUEADMIN_HEADER_LOGOMINI')
        },
        "alt": "logo"
    }
    return mark_safe(json.dumps(logo, cls=LazyEncoder))


@register.simple_tag
def vue_toolbox():
    toolbox = {
        "lock": {
            "enable": vsettings.get_config('VUEADMIN_HEADER_TOOLBOX_LOCK'),
            "verify": "email"
        },
        "github": {
            "enable": vsettings.get_config('VUEADMIN_HEADER_TOOLBOX_GITHUB'),
            "link": "https://github.com/ryuchen"
        },
        "search": {
            "enable": vsettings.get_config('VUEADMIN_HEADER_TOOLBOX_SEARCH'),
        },
        "notice": {
            "enable": vsettings.get_config('VUEADMIN_HEADER_TOOLBOX_NOTICE'),
        },
        "utility": {
            "enable": vsettings.get_config('VUEADMIN_HEADER_TOOLBOX_UTILITY'),
        }
    }
    return mark_safe(json.dumps(toolbox, cls=LazyEncoder))


@register.simple_tag
def vue_footer():
    footer = {
        "author": "Ryuchen",
        "year": datetime.datetime.now().year,
        "link": "https://github.com/ryuchen"
    }
    year = __get_config('VUEADMIN_FOOTER_COPYRIGHT_YEAR')
    if year is not None:
        footer["year"] = year

    author = __get_config('VUEADMIN_FOOTER_COPYRIGHT_AUTHOR')
    if author is not None:
        footer["author"] = author

    link = __get_config('VUEADMIN_FOOTER_COPYRIGHT_LINK')
    if link is not None:
        footer["link"] = link

    return mark_safe(json.dumps(footer, cls=LazyEncoder))


@register.simple_tag(takes_context=True)
def adv_search_placeholder(context):
    cl = context.get('cl')
    verboses = []

    # 取消递归，只获取2级
    if cl:
        for sf in cl.search_fields:
            verboses.append(_field_display(cl.model, sf))

    return mark_safe("，".join(verboses))


@register.simple_tag
def adv_list_filter(cl, spec):
    list_filter = {
        'title': spec.title,
        'choices': list(spec.choices(cl)),
    }
    return mark_safe(json.dumps(list_filter, cls=LazyEncoder))


@register.filter
def config(key):
    return __get_config(key)


@register.filter
def vue_debug(value):
    return value


# ############################## overwrite django admin default tags ################################
DOT = '.'


@register.simple_tag
def paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == DOT:
        return '… '
    elif i == cl.page_num:
        return format_html('<span class="this-page">{}</span> ', i + 1)
    else:
        return format_html(
            '<a href="{}"{}>{}</a> ',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe(' class="end"' if i == cl.paginator.num_pages - 1 else ''),
            i + 1,
        )


@register.simple_tag(name='adv_pagination')
def pagination_tag(cl):
    """
    Generate the series of links to the pages in a paginated list.
    """
    paginator, page_num = cl.paginator, cl.page_num
    return mark_safe(json.dumps({
        'current': page_num,
        'total': paginator.count,
        'link': cl.get_query_string({PAGE_VAR: page_num}),
        'size': 20
    }))


def result_headers(cl):
    """
    Generate the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model,
            model_admin=cl.model_admin,
            return_attr=True
        )
        is_field_sortable = cl.sortable_by is None or field_name in cl.sortable_by
        if attr:
            field_name = _coerce_field_name(field_name, i)
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == 'action_checkbox':
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            if not admin_order_field:
                is_field_sortable = False

        if not is_field_sortable:
            # Not sortable
            yield {
                'text': text,
                'sortable': False,
            }
            continue

        # OK, it is sortable if we got this far
        th_classes = ['sortable', 'column-{}'.format(field_name)]
        order_type = ''
        new_order_type = 'asc'
        sort_priority = 0
        # Is it currently being sorted on?
        is_sorted = i in ordering_field_columns
        if is_sorted:
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append('sorted %sending' % order_type)
            new_order_type = {'asc': 'desc', 'desc': 'asc'}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field

        def make_qs_param(t, n):
            return ('-' if t == 'desc' else '') + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "title": text,
            "dataIndex": text,
            "sorter": True,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string({ORDER_VAR: '.'.join(o_list_primary)}),
            "url_remove": cl.get_query_string({ORDER_VAR: '.'.join(o_list_remove)}),
            "url_toggle": cl.get_query_string({ORDER_VAR: '.'.join(o_list_toggle)}),
        }


def _boolean_icon(field_val):
    icon_url = static('admin/img/icon-%s.svg' % {True: 'yes', False: 'no', None: 'unknown'}[field_val])
    return format_html('<img src="{}" alt="{}">', icon_url, field_val)


def _coerce_field_name(field_name, field_index):
    """
    Coerce a field_name (which may be a callable) to a string.
    """
    if callable(field_name):
        if field_name.__name__ == '<lambda>':
            return 'lambda' + str(field_index)
        else:
            return field_name.__name__
    return field_name


def items_for_result(cl, result, form):
    """
    Generate the actual list of data.
    """

    def link_in_col(is_first, field_name, cl):
        if cl.list_display_links is None:
            return False
        if is_first and not cl.list_display_links:
            return True
        return field_name in cl.list_display_links

    first = True
    pk = cl.lookup_opts.pk.attname  # primary key
    for field_index, field_name in enumerate(cl.list_display):
        empty_value_display = cl.model_admin.get_empty_value_display()
        row_classes = ['field-%s' % _coerce_field_name(field_name, field_index)]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(attr, 'empty_value_display', empty_value_display)
            if f is None or f.auto_created:
                if field_name == 'action_checkbox':
                    row_classes = ['action-checkbox']
                boolean = getattr(attr, 'boolean', False)
                result_repr = display_for_value(value, empty_value_display, boolean)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append('nowrap')
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f, empty_value_display)
                if isinstance(f, (models.DateField, models.TimeField, models.ForeignKey)):
                    row_classes.append('nowrap')
        if str(result_repr) == '':
            result_repr = mark_safe('&nbsp;')
        row_class = mark_safe(' class="%s"' % ' '.join(row_classes))
        # If list_display_links not defined, add the link tag to the first field
        if link_in_col(first, field_name, cl):
            table_tag = 'th' if first else 'td'
            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                url = add_preserved_filters({'preserved_filters': cl.preserved_filters, 'opts': cl.opts}, url)
                # Convert the pk to something that can be used in Javascript.
                # Problem cases are non-ASCII strings.
                if cl.to_field:
                    attr = str(cl.to_field)
                else:
                    attr = pk
                value = result.serializable_value(attr)
                link_or_text = format_html(
                    '<a href="{}"{}>{}</a>',
                    url,
                    format_html(
                        ' data-popup-opener="{}"', value
                    ) if cl.is_popup else '',
                    result_repr)

            yield format_html('<{}{}>{}</{}>', table_tag, row_class, link_or_text, table_tag)
        else:
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (form and field_name in form.fields and not (
                    field_name == cl.model._meta.pk.name and
                    form[cl.model._meta.pk.name].is_hidden)):
                bf = form[field_name]
                result_repr = mark_safe(str(bf.errors) + str(bf))
            yield format_html('{}', result_repr)
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html('{}', form[cl.model._meta.pk.name])


class ResultList(list):
    """
    Wrapper class used to return items in a list_editable changelist, annotated
    with the form object for error reporting purposes. Needed to maintain
    backwards compatibility with existing admin templates.
    """

    def __init__(self, form, *items):
        self.form = form
        super().__init__(*items)


def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield ResultList(form, items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield ResultList(None, items_for_result(cl, res, None))


def result_hidden_fields(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            if form[cl.model._meta.pk.name].is_hidden:
                yield mark_safe(form[cl.model._meta.pk.name])


@register.simple_tag(name='adv_result_header')
def result_header(cl):
    """
    Display the headers.
    """
    return mark_safe(json.dumps(list(result_headers(cl))))


@register.simple_tag(name='adv_result_list')
def result_list(cl):
    """
    Display data list.
    """
    return mark_safe(json.dumps(list(results(cl))))

# ############################## overwrite django admin default tags ################################
