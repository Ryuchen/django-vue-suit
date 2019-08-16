from django.apps import AppConfig


class CultivateConfig(AppConfig):
    name = 'app'
    verbose_name = '培养管理'
    verbose_name_plural = verbose_name

    # vueAdmin settings
    vueAdmin_icon = 'user'
