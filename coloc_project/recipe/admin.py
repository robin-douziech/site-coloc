from django.contrib import admin

from . import models
# Register your models here.

@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
	filter_horizontal = ('utensils', 'tags')

@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
	pass

@admin.register(models.Utensil)
class UtensilAdmin(admin.ModelAdmin):
	pass

@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
	pass

@admin.register(models.Step)
class StepAdmin(admin.ModelAdmin):
	pass

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
	pass

@admin.register(models.RecipeIngredientRelationship)
class RecipeIngredientRelationshipAdmin(admin.ModelAdmin):
	pass