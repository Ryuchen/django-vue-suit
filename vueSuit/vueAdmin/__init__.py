#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================

from django.utils.module_loading import autodiscover_modules

from .decorators import register
from .filters import (
    AllValuesFieldListFilter, BooleanFieldListFilter, ChoicesFieldListFilter,
    DateFieldListFilter, FieldListFilter, ListFilter, RelatedFieldListFilter,
    RelatedOnlyFieldListFilter, SimpleListFilter,
)
from .options import (
    HORIZONTAL, VERTICAL, ModelAdmin, StackedInline, TabularInline,
)
from .sites import AdminSite, site

__all__ = [
    "register", "ModelAdmin", "HORIZONTAL", "VERTICAL",
    "StackedInline", "TabularInline", "AdminSite", "site", "ListFilter",
    "SimpleListFilter", "FieldListFilter", "BooleanFieldListFilter",
    "RelatedFieldListFilter", "ChoicesFieldListFilter", "DateFieldListFilter",
    "AllValuesFieldListFilter", "RelatedOnlyFieldListFilter", "autodiscover",
]


def autodiscover():
    autodiscover_modules('vueAdmin', register_to=site)


default_app_config = 'vueSuit.vueAdmin.apps.VueAdminConfig'
