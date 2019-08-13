#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================

from django.apps import AppConfig
from django.core import checks
from django.utils.translation import gettext_lazy as _

from .checks import check_admin_app, check_dependencies


class SimpleAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    default_site = 'vueSuit.vueAdmin.sites.AdminSite'
    name = 'vueSuit.vueAdmin'
    verbose_name = _("Administration")

    def ready(self):
        checks.register(check_dependencies, checks.Tags.admin)
        checks.register(check_admin_app, checks.Tags.admin)


class VueAdminConfig(SimpleAdminConfig):
    """The default AppConfig for admin which does auto discovery."""

    def ready(self):
        super().ready()
        self.module.autodiscover()
