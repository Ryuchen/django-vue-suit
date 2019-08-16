from functools import update_wrapper
from weakref import WeakSet

from django.apps import apps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.exceptions import ImproperlyConfigured
from django.db.models.base import ModelBase
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django.urls import NoReverseMatch, reverse
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django.utils.text import capfirst
from django.utils.translation import gettext as _, gettext_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.i18n import JavaScriptCatalog

from . import ModelAdmin
from .settings import VueAdminSettings


all_sites = WeakSet()


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class AdminSite:
    """
    An VueAdminSite object encapsulates an instance of the Django admin application rewrite
    by Ant Design Vue, ready to be hooked in to your URL conf. Models are registered with the
    VueAdminSite using the register() method, and the get_urls() method can then be used to
    access Vue view functions that present a full admin interface for the collection of registered
    models.
    """

    # Text to put at the end of each page's <title>.
    site_title = gettext_lazy('Django site admin')

    # Text to put in each page's <h1>.
    site_header = gettext_lazy('Django administration')

    # Text to put at the top of the admin index page.
    index_title = gettext_lazy('Site administration')

    # URL for the "View site" link at the top of each admin page.
    site_url = '/'

    _empty_value_display = '-'

    index_template = None
    app_index_template = None

    login_form = None
    login_template = None
    logout_template = None
    password_reset_form = None
    password_reset_template = None
    password_reset_done_template = None
    password_change_form = None
    password_change_template = None
    password_change_done_template = None

    def __init__(self, name='vueAdmin'):
        self.name = name
        self._registry = {}  # model_class class -> admin_class instance
        self._actions = {}
        self._global_actions = self._actions.copy()
        self._settings = VueAdminSettings()
        all_sites.add(self)

    def check(self, app_configs):
        """
        Run the system checks on all ModelAdmins, except if they aren't
        customized at all.
        """
        if app_configs is None:
            app_configs = apps.get_app_configs()
        app_configs = set(app_configs)  # Speed up lookups below

        errors = []
        modeladmins = (o for o in self._registry.values() if o.__class__ is not ModelAdmin)
        for modeladmin in modeladmins:
            if modeladmin.model._meta.app_config in app_configs:
                errors.extend(modeladmin.check())
        return errors

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Register the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, use ModelAdmin (the default admin
        options). If keyword arguments are given -- e.g., list_display --
        apply them as options to the admin class.

        If a model is already registered, raise AlreadyRegistered.

        If a model is abstract, raise ImproperlyConfigured.
        """
        admin_class = admin_class or ModelAdmin
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    'The model %s is abstract, so it cannot be registered with admin.' % model.__name__
                )

            if model in self._registry:
                raise AlreadyRegistered('The model %s is already registered' % model.__name__)

            # Ignore the registration if the model has been
            # swapped out.
            if not model._meta.swapped:
                # If we got **options then dynamically construct a subclass of
                # admin_class with those **options.
                if options:
                    # For reasons I don't quite understand, without a __module__
                    # the created class appears to "live" in the wrong place,
                    # which causes issues later on.
                    options['__module__'] = __name__
                    admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)

                # Instantiate the admin class to save in the registry
                self._registry[model] = admin_class(model, self)

    def unregister(self, model_or_iterable):
        """
        Unregister the given model(s).

        If a model isn't already registered, raise NotRegistered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]

    def is_registered(self, model):
        """
        Check if a model class is registered with this `AdminSite`.
        """
        return model in self._registry

    def add_action(self, action, name=None):
        """
        Register an action to be available globally.
        """
        name = name or action.__name__
        self._actions[name] = action
        self._global_actions[name] = action

    def disable_action(self, name):
        """
        Disable a globally-registered action. Raise KeyError for invalid names.
        """
        del self._actions[name]

    def get_action(self, name):
        """
        Explicitly get a registered global action whether it's enabled or
        not. Raise KeyError for invalid names.
        """
        return self._global_actions[name]

    @property
    def actions(self):
        """
        Get all the enabled actions as an iterable of (name, func).
        """
        return self._actions.items()

    @property
    def empty_value_display(self):
        return self._empty_value_display

    @empty_value_display.setter
    def empty_value_display(self, empty_value_display):
        self._empty_value_display = empty_value_display

    @staticmethod
    def has_permission(request):
        """
        Return True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active and request.user.is_staff

    def admin_view(self, view, cacheable=False):
        """
        Decorator to create an admin view attached to this ``AdminSite``. This
        wraps the view and provides permission checking by calling
        ``self.has_permission``.

        You'll want to use this from within ``AdminSite.get_urls()``:

            class MyAdminSite(AdminSite):

                def get_urls(self):
                    from django.urls import path

                    urls = super().get_urls()
                    urls += [
                        path('my_view/', self.admin_view(some_view))
                    ]
                    return urls

        By default, admin_views are marked non-cacheable using the
        ``never_cache`` decorator. If the view can be safely cached, set
        cacheable=True.
        """
        def inner(request, *args, **kwargs):
            if not self.has_permission(request):
                if request.path == reverse('admin:logout', current_app=self.name):
                    index_path = reverse('admin:index', current_app=self.name)
                    return HttpResponseRedirect(index_path)
                # Inner import to prevent django.contrib.admin (app) from
                # importing django.contrib.auth.models.User (unrelated model).
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(
                    request.get_full_path(),
                    reverse('admin:login', current_app=self.name)
                )
            return view(request, *args, **kwargs)
        if not cacheable:
            inner = never_cache(inner)
        # We add csrf_protect here so this function can be used as a utility
        # function for any view, without having to repeat 'csrf_protect'.
        if not getattr(view, 'csrf_exempt', False):
            inner = csrf_protect(inner)
        return update_wrapper(inner, view)

    def get_urls(self):
        from django.urls import include, path
        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.contenttypes.views imports ContentType.

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = [
            path('', wrap(self.index), name='index'),
            path('login/', self.login, name='login'),
            path('logout/', wrap(self.logout), name='logout'),
            path('password_reset/', self.password_reset, name='password_reset'),
            path('password_reset_done/', self.password_reset_done, name='password_reset_done'),
            path('password_change/', wrap(self.password_change, cacheable=True), name='password_change'),
            path('password_change/done/', wrap(self.password_change_done, cacheable=True), name='password_change_done'),
            path('jsi18n/', wrap(self.i18n_javascript, cacheable=True), name='jsi18n'),
            path('dashboard', wrap(self.dashboard, cacheable=True), name='dashboard'),
        ]

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        valid_app_labels = []
        for model, model_admin in self._registry.items():
            urlpatterns += [
                path('%s/%s/' % (model._meta.app_label, model._meta.model_name), include(model_admin.urls)),
            ]
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'admin', self.name

    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.

        For sites running on a subpath, use the SCRIPT_NAME value if site_url
        hasn't been customized.
        """
        script_name = request.META['SCRIPT_NAME']
        site_url = script_name if self.site_url == '/' and script_name else self.site_url
        return {
            'site_title': self.site_title,
            'site_header': self.site_header,
            'site_url': site_url,
            'has_permission': self.has_permission(request),
            'available_apps': self.get_app_list(request),
            'is_popup': False,
        }

    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {
                m: m_a for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            app_label = model._meta.app_label

            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                'name': capfirst(model._meta.verbose_name_plural),
                'object_name': model._meta.object_name,
                'icon': '',
                'perms': perms,
                'admin_url': None,
                'add_url': None,
            }

            if hasattr(model, 'vueAdmin_icon'):
                model_dict['icon'] = model.vueAdmin_icon()

            if perms.get('change') or perms.get('view'):
                model_dict['view_only'] = not perms.get('change')
                try:
                    model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                except NoReverseMatch:
                    pass
            if perms.get('add'):
                try:
                    model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                except NoReverseMatch:
                    pass

            if app_label in app_dict:
                app_dict[app_label]['models'].append(model_dict)
            else:
                app_dict[app_label] = {
                    'name': apps.get_app_config(app_label).verbose_name,
                    'icon': apps.get_app_config(app_label).vueAdmin_icon,
                    'app_label': app_label,
                    'has_module_perms': has_module_perms,
                    'models': [model_dict],
                }
        if label:
            return app_dict.get(label)
        return app_dict

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list

    @never_cache
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)

        context = {
            **self.each_context(request),
            'title': self.index_title,
            'app_list': app_list,
            **(extra_context or {}),
        }

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'vueAdmin/pages/index.html', context)

    def dashboard(self, request, extra_context=None):
        """
        Log in dashboard display for the setting home page type
        :param request:
        :param extra_context:
        :return:
        """
        app_list = self.get_app_list(request)

        from .views.views import DashboardWorkPlaceView, DashboardOverviewView
        context = {
            **self.each_context(request),
            'app_list': app_list,
            **(extra_context or {})
        }
        # No display form
        defaults = {
            'extra_context': context,
        }
        request.current_app = self.name

        dashboard = self._settings.get_config("VUEADMIN_HOME_TYPE")
        if dashboard == "Workplace":
            return DashboardWorkPlaceView.as_view(**defaults)(request)
        else:
            return DashboardOverviewView.as_view(**defaults)(request)

    @never_cache
    def login(self, request, extra_context=None):
        """
        Display the login form for the given HttpRequest.
        """
        if request.method == 'GET' and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse('admin:index', current_app=self.name)
            return HttpResponseRedirect(index_path)

        from django.contrib.auth.views import LoginView  # Django Auth View
        context = {
            **self.each_context(request),
            'title': _('Log in'),
            'app_path': request.get_full_path(),
            'username': request.user.get_username(),
        }
        if REDIRECT_FIELD_NAME not in request.GET and REDIRECT_FIELD_NAME not in request.POST:
            context[REDIRECT_FIELD_NAME] = reverse('admin:index', current_app=self.name)
        context.update(extra_context or {})

        from .forms import AdminAuthenticationForm  # Define AdminAuthenticationForm
        defaults = {
            'extra_context': context,
            'form_class': self.login_form or AdminAuthenticationForm,
            'template_name': self.login_template or 'vueAdmin/pages/passport/login.html',
        }
        request.current_app = self.name
        return LoginView.as_view(**defaults)(request)

    @never_cache
    def logout(self, request, extra_context=None):
        """
        Log out the user for the given HttpRequest.
        This should *not* assume the user is already logged in.
        """
        from django.contrib.auth.views import LogoutView
        context = {
            **self.each_context(request),
            'title': _('Log out'),
            # Since the user isn't logged out at this point, the value of
            # has_permission must be overridden.
            'has_permission': False,
            **(extra_context or {})
        }
        # No display form
        defaults = {
            'extra_context': context,
            'template_name': self.logout_template or 'vueAdmin/pages/passport/logout.html',
        }
        request.current_app = self.name
        return LogoutView.as_view(**defaults)(request)

    def password_reset(self, request, extra_context=None):
        """
        Handle the "reset password" task -- both form display and validation.
        """
        from django.contrib.auth.views import PasswordResetView
        context = {
            **self.each_context(request),
            'title': _('Password reset'),
            **(extra_context or {})
        }
        from .forms import PasswordResetForm
        url = reverse('admin:password_reset_done', current_app=self.name)
        defaults = {
            'extra_context': context,
            'form_class': self.password_reset_form or PasswordResetForm,
            'success_url': url,
            'template_name': self.password_reset_template or 'vueAdmin/pages/passport/password_reset_form.html',
        }
        request.current_app = self.name
        return PasswordResetView.as_view(**defaults)(request)

    def password_reset_done(self, request, extra_context=None):
        from django.contrib.auth.views import PasswordResetDoneView
        defaults = {
            'extra_context': {**self.each_context(request), **(extra_context or {})},
            'template_name': self.password_change_done_template or 'vueAdmin/pages/passport/password_reset_done.html'
        }
        request.current_app = self.name
        return PasswordResetDoneView.as_view(**defaults)(request)

    def password_change(self, request, extra_context=None):
        """
        Handle the "change password" task -- both form display and validation.
        """
        from .forms import AdminPasswordChangeForm
        from django.contrib.auth.views import PasswordChangeView
        url = reverse('admin:password_change_done', current_app=self.name)
        defaults = {
            'form_class': AdminPasswordChangeForm,
            'success_url': url,
            'extra_context': {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_change_template is not None:
            defaults['template_name'] = self.password_change_template
        request.current_app = self.name
        return PasswordChangeView.as_view(**defaults)(request)

    def password_change_done(self, request, extra_context=None):
        """
        Display the "success" page after a password change.
        """
        from django.contrib.auth.views import PasswordChangeDoneView
        defaults = {
            'extra_context': {**self.each_context(request), **(extra_context or {})},
        }
        if self.password_change_done_template is not None:
            defaults['template_name'] = self.password_change_done_template
        request.current_app = self.name
        return PasswordChangeDoneView.as_view(**defaults)(request)

    def i18n_javascript(self, request, extra_context=None):
        """
        Display the i18n JavaScript that the Django admin requires.

        `extra_context` is unused but present for consistency with the other
        admin views.
        """
        return JavaScriptCatalog.as_view(packages=['vueSuit.vueAdmin'])(request)


class DefaultAdminSite(LazyObject):
    def _setup(self):
        admin_site_class = import_string(apps.get_app_config('vueAdmin').default_site)
        self._wrapped = admin_site_class()


# This global object represents the default admin site, for the common case.
# You can provide your own AdminSite using the (Simple)AdminConfig.default_site
# attribute. You can also instantiate AdminSite in your own code to create a
# custom admin site.
site = DefaultAdminSite()
