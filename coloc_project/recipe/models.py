from django.db import models
from datetime import timedelta
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
import shutil

def recipe_name(instance, filename):
	return f"recipe/{instance.id}/image.jpg"

def ingredient_name(instance, filename):
	return f"ingredient/{instance.id}/image.jpg"

def utensil_name(instance, filename):
	return f"utensil/{instance.id}/image.jpg"

class Tag(models.Model):
	
	text = models.CharField(
		verbose_name = "Texte",
		max_length = 50,
		default = "Tag sans texte"
	)

	def __str__(self):
		return self.text

class Ingredient(models.Model):
	
	name = models.CharField(
		verbose_name = "Nom",
		max_length = 50,
		default = "Ingrédient sans nom"
	)

	image = models.ImageField(
		verbose_name = "Image",
		upload_to = ingredient_name,
		null = True,
		blank = True
	)

	def delete(self, *args, **kwargs):
		shutil.rmtree(f"{settings.MEDIA_ROOT}{self.image.url.split('/', 2)[2][::-1].split('/', 1)[1][::-1]}/")
		super(Ingredient, self).delete(*args, **kwargs)

	def __str__(self):
		return self.name

class Utensil(models.Model):
	
	name = models.CharField(
		verbose_name = "Nom",
		max_length = 50,
		default = "Ustensile sans nom"
	)

	image = models.ImageField(
		verbose_name = "Image",
		upload_to = utensil_name,
		null = True,
		blank = True
	)

	def delete(self, *args, **kwargs):
		shutil.rmtree(f"{settings.MEDIA_ROOT}{self.image.url.split('/', 2)[2][::-1].split('/', 1)[1][::-1]}/")
		super(Utensil, self).delete(*args, **kwargs)

	def __str__(self):
		return self.name

class Recipe(models.Model):

	title = models.CharField(
		verbose_name = "Titre",
		max_length = 100,
		default = "Recette sans titre"
	)

	prep_duration = models.DurationField(
		verbose_name = "Préparation",
		default = timedelta(minutes=0),
		validators = [RegexValidator(r"^([0-9]{1,2}:[0-5][0-9]:[0-5][0-9])$")]
	)

	cook_duration = models.DurationField(
		verbose_name = "Cuisson",
		default = timedelta(minutes=0),
		validators = [RegexValidator(r"^([0-9]{1,2}:[0-5][0-9]:[0-5][0-9])$")]
	)

	nb_pers = models.IntegerField(
		verbose_name = "Nombre de parts",
		validators = [MinValueValidator(1), MaxValueValidator(20)],
		default = 1
	)

	difficulty = models.IntegerField(
		verbose_name = "Difficulté",
		validators = [MinValueValidator(0), MaxValueValidator(10)],
		default = 0
	)

	grade = models.IntegerField(
		verbose_name = "Note",
		validators = [MinValueValidator(0), MaxValueValidator(10)],
		default = 0
	)

	image = models.ImageField(
		verbose_name = "Image",
		upload_to = recipe_name,
		null = True,
		blank = True
	)

	ingredients = models.ManyToManyField(
		Ingredient,
		through = "RecipeIngredientRelationship",
		verbose_name = "Ingrédients",
		blank = True,
		related_name = "recipes"
	)

	utensils = models.ManyToManyField(
		Utensil,
		verbose_name = "Ustensiles",
		blank = True,
		related_name = "recipes"
	)

	tags = models.ManyToManyField(
		Tag,
		verbose_name = "Tags",
		blank = True,
		related_name = "recipes"
	)

	def delete(self, *args, **kwargs):
		shutil.rmtree(f"{settings.MEDIA_ROOT}{self.image.url.split('/', 2)[2][::-1].split('/', 1)[1][::-1]}/")
		super(Recipe, self).delete(*args, **kwargs)

	def __str__(self):
		return self.title

class Step(models.Model):
	
	text = models.CharField(
		verbose_name = "Texte",
		max_length = 300,
		default = ""
	)

	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')

	def __str__(self):
		return f"{list(self.recipe.steps.all()).index(self)+1}) {self.recipe.title}"

class Comment(models.Model):
	
	text = models.CharField(
		verbose_name = "Texte",
		max_length = 300,
		default = ""
	)

	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')

	def __str__(self):
		return f"{self.recipe.title} : {self.text[:min([10, len(self.text)])]}{'...' if len(self.text)>10 else ''}"

class RecipeIngredientRelationship(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredient_relationships")
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipe_relationships")
	quantity = models.CharField(
		verbose_name = "Quantité",
		max_length = 20,
		validators = [RegexValidator(r"^(([1-9][0-9]*|0)([.,][0-9]*){0,1}( g| kg| L| cL | dL| càs| càc){0,1})$")],
		default = "0 g"
	)

	def __str__(self):
		return f"{self.recipe.title} : {self.ingredient.name} ({self.quantity})"