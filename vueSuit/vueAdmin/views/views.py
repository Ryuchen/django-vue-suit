#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _


class DashboardWorkPlaceView(TemplateView):
    template_name = 'vueAdmin/pages/dashboard/workplace.html'
    title = _('Workplace')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class DashboardOverviewView(TemplateView):
    template_name = 'vueAdmin/pages/dashboard/overview.html'
    title = _('Overview')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
