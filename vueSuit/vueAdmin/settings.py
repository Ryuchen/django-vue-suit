#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================
import os

from django.conf import settings


class VueAdminSettings:
    VUEADMIN_DEFAULT = {
        'VUEADMIN_HOME_TYPE': 'Workplace'
    }

    def get_config(self, name):
        value = os.environ.get(name, getattr(settings, name, None))
        if value is None:
            value = self.VUEADMIN_DEFAULT.get(name, None)
        return value
