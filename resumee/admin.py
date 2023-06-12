from django.contrib import admin
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.contrib.admin.actions import delete_selected
# Register your models here.

from .models import *


def activate_resume(modeladmin, request, queryset):
    try:
        if queryset.count() == 1:
            queryset[0].activate()
    except AttributeError:
        return


activate_resume.short_description = "Activates selected resume"


def duplicate_resume(modeladmin, request, queryset):
    try:
        for query in queryset:
            query.duplicate()
    except AttributeError:
        return


duplicate_resume.short_description = "Duplicates selected resume"

admin.site.add_action(activate_resume)
admin.site.add_action(duplicate_resume)

admin.site.register(Referee)


class ResumeeAdmin(admin.ModelAdmin):
    actions_on_top = True
    model = Resumee
    list_display = ('id', 'first_name', "middle_name", "surname", "active")
    list_filter = ('template', )
    search_fields = ("first_name", "surname", "middle_name", "email")
    ordering = ("id", "surname", "first_name")


admin.site.register(WorkExperience)
admin.site.register(WorkExperienceDescription)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Job)
admin.site.register(Portfolio)
admin.site.register(PortfolioImage)
admin.site.register(Language)


admin.site.register(Resumee, ResumeeAdmin)

admin.site.register(Template)
