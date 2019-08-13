#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================

from django.core.exceptions import SuspiciousOperation


class DisallowedModelAdminLookup(SuspiciousOperation):
    """Invalid filter was passed to admin view via URL querystring"""
    pass


class DisallowedModelAdminToField(SuspiciousOperation):
    """Invalid to_field was passed to admin view via URL query string"""
    pass
