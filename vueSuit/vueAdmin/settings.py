#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================
import os

from django.conf import settings


class VueAdminSettings:
    VUEADMIN_DEFAULT = {
        # Common settings
        'GITHUB_URL': 'https://github.com/ryuchen',

        # HOME_PAGE Display style
        'VUEADMIN_HOME_TYPE': 'Workplace',

        # Global site logo
        'VUEADMIN_HEADER_LOGOFULL': settings.STATIC_URL + "vueAdmin/img/logo-full.png",
        'VUEADMIN_HEADER_LOGOMINI': settings.STATIC_URL + "vueAdmin/img/logo-mini.png",

        # Site Header Toolbox setting
        'VUEADMIN_HEADER_TOOLBOX_LOCK': True,
        'VUEADMIN_HEADER_TOOLBOX_GITHUB': True,
        'VUEADMIN_HEADER_TOOLBOX_SEARCH': False,
        'VUEADMIN_HEADER_TOOLBOX_NOTICE': True,
        'VUEADMIN_HEADER_TOOLBOX_UTILITY': True,
    }

    def get_config(self, name):
        value = os.environ.get(name, getattr(settings, name, None))
        if value is None:
            value = self.VUEADMIN_DEFAULT.get(name, None)
        return value
