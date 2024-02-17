from django.contrib import admin
from . import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
	filter_horizontal = ('groups', 'user_permissions')