from django.contrib import admin

from . import models

@admin.register(models.ImageModel)
class ImageAdmin(admin.ModelAdmin):
	pass