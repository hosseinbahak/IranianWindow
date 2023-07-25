from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin

@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'employee', 'employer', 'check_date', 'state')
    list_filter = ('employee', 'state')

@admin.register(ProjectCheckDateHistory)
class ProjectCheckDateHistoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'timestamp')


