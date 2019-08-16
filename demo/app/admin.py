# Register your models here.

from . import models

from vueSuit import vueAdmin


class ThesisPlaCheckInline(vueAdmin.TabularInline):
    verbose_name = '查重结果'
    verbose_name_plural = verbose_name
    model = models.ThesisPlaCheck
    extra = 0


class ThesisBlindReviewInline(vueAdmin.TabularInline):
    verbose_name = '盲审结果'
    verbose_name_plural = verbose_name
    model = models.ThesisBlindReview
    extra = 0


class ThesisAdmin(vueAdmin.ModelAdmin):
    actions_on_top = True
    list_filter = [
        'the_is_superb',
        'the_start_result',
        'the_is_delay'
    ]
    list_display = (
        'get_thesis_title', 'the_start_time', 'the_start_result', 'the_is_delay', 'the_delay_reason',
        'the_is_superb', 'the_final_score'
    )
    inlines = [
        ThesisPlaCheckInline,
        ThesisBlindReviewInline
    ]
    list_per_page = 20
    date_hierarchy = 'the_start_time'
    search_fields = ('the_title', )
    empty_value_display = '--'


class ThesisPlaCheckAdmin(vueAdmin.ModelAdmin):
    list_filter = [
        'pla_result',
    ]
    list_display = (
        'pla_date', 'pla_result', 'pla_rate', 'pla_thesis'
    )
    list_per_page = 20
    date_hierarchy = 'pla_date'
    empty_value_display = '--'


class ThesisBlindReviewAdmin(vueAdmin.ModelAdmin):
    list_filter = [
        'bli_score',
    ]
    list_display = (
        'bli_date', 'bli_score', 'bli_thesis'
    )
    list_per_page = 20
    date_hierarchy = 'bli_date'
    empty_value_display = '--'


# Register your models here.
vueAdmin.site.register(models.Thesis, ThesisAdmin)
vueAdmin.site.register(models.ThesisPlaCheck, ThesisPlaCheckAdmin)
vueAdmin.site.register(models.ThesisBlindReview, ThesisBlindReviewAdmin)
