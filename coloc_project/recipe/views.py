from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.db.models import F
from datetime import timedelta, datetime
from django.http import HttpResponse
import logging

from coloc import helpers
from . import models, forms

# views that handle forms.MyCreateModelForm forms
def my_model_form_view(request, form_class, template_name):
	form = form_class()
	model = form.Meta.model
	if request.method == "POST":
		form = form_class(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('/coloc/back?nb=1')
	return render(request, template_name, {'form': form, model.__name__.lower()+'s': model.objects.order_by(model._meta.fields[1].name)})

@login_required
@permission_required('recipe.add_recipe')
def create_recipe(request):
	return my_model_form_view(request, forms.CreateRecipeForm, "recipe/create/recipe.html")

@login_required
@permission_required('recipe.add_ingredient')
def create_ingredient(request):
	return my_model_form_view(request, forms.CreateIngredientForm, "recipe/create/ingredient.html")

@login_required
@permission_required('recipe.add_utensil')
def create_utensil(request):
	return my_model_form_view(request, forms.CreateUtensilForm, "recipe/create/utensil.html")

@login_required
@permission_required('recipe.add_tag')
def create_tag(request):
	return my_model_form_view(request, forms.CreateTagForm, "recipe/create/tag.html")

def list(request):

	#request.session.pop('search_recipe')

	current_page = reverse('recipe:list')

	request.session['search_recipe'] = request.session.get('search_recipe', {
		'search': "",
		'max_duration': "",
		'seasonal': False,
		'ingredients': [],
		'tags': []
	})	

	initial_data = {
		'search': request.GET.get('search', request.session['search_recipe']['search']),
		'max_duration': request.GET.get('max_duration', request.session['search_recipe']['max_duration']),
		'seasonal': True if request.GET.get('seasonal', '')=="on" else False,
		'ingredient': None
	}

	get_forms = {
		'search_form': forms.SearchRecipeForm(request, request.GET, initial=initial_data),
	}

	post_forms = {
		'ingredient_form': forms.SelectIngredientForm(request),
		'tag_form': forms.SelectTagForm(request)
	}

	if request.method == "POST":
		post_forms = {
			'ingredient_form': forms.SelectIngredientForm(request, request.POST),
			'tag_form': forms.SelectTagForm(request, request.POST)
		}
		for form in post_forms :
			if post_forms[form].is_valid():
				post_forms[form].save(request)

		return redirect(reverse('recipe:list'))

	elif request.method == "GET":
		for form in get_forms:
			if get_forms[form].is_valid():
				get_forms[form].save(request)

	### Recherche des recettes correspondant aux critères de recherche

	results = models.Recipe.objects.filter(title__icontains=request.session['search_recipe']['search']).order_by("title")

	# gestion des ingrédients et des tags :
	# si des ingrédients et/ou des tags sont renseignés, on ne garde que les recettes comporant au moins l'un des ingrédients ET au moins l'un des tags
	if len(request.session['search_recipe']['ingredients']+request.session['search_recipe']['tags']) > 0:
		if len(request.session['search_recipe']['ingredients']) > 0 :
			results = results.filter(ingredients__id__in=request.session['search_recipe']['ingredients']).distinct()
		if len(request.session['search_recipe']['tags']) > 0 :
			results = results.filter(tags__id__in=request.session['search_recipe']['tags']).distinct()

	# On supprime les recettes trop longues si le champ "Durée maximale" est renseigné
	if request.session['search_recipe']['max_duration'] != "" :
		max_duration = timedelta(
			hours = int(request.session['search_recipe']['max_duration'].split(':')[0]),
			minutes = int(request.session['search_recipe']['max_duration'].split(':')[1]),
			seconds = int(request.session['search_recipe']['max_duration'].split(':')[2]),
		)
		results = results.filter(prep_duration__lte=max_duration-F('cook_duration'))

	# On supprime les recettes qui ne sont pas de saison si "recettes de saison uniquement" est coché
	if request.session['search_recipe']['seasonal']:
		current_month = int(datetime.now().strftime('%m'))
		for recipe in results :
			for ingredient in recipe.ingredients.all():
				if ingredient.months is not None :
					month = int(ingredient.months.split('-')[0])
					end = int(ingredient.months.split('-')[1])
					while month not in [current_month, end]:
						month = month+1 if month<12 else 1
					if month == end :
						results = results.exclude(pk=recipe.id)
						break
					else :
						continue

	ingredients = models.Ingredient.objects.filter(pk__in=request.session['search_recipe']['ingredients']).order_by("name")
	tags = models.Tag.objects.filter(pk__in=request.session['search_recipe']['tags']).order_by("text")

	helpers.register_view(request, current_page)
	return render(request, "recipe/list.html", {
		'results': results,
		**get_forms,
		**post_forms,
		'ingredients': ingredients,
		'tags': tags
	})

def details(request):
	recipe_id = request.GET.get('id', False)
	if recipe_id:
		recipe = get_object_or_404(models.Recipe, pk=recipe_id)
		current_page = f"{reverse('recipe:details')}?id={recipe_id}"
		helpers.register_view(request, current_page)
		return render(request, "recipe/details.html", {'recipe': recipe})
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.change_recipe')
def edit(request):
	recipe_id = request.GET.get('id', False)
	if recipe_id:
		recipe = get_object_or_404(models.Recipe, pk=recipe_id)
		current_page = f"{reverse('recipe:edit')}?id={recipe_id}"
		forms_dic = {
			'prep_duration_form': forms.ChangePrepDurationForm(instance=recipe),
			'cook_duration_form': forms.ChangeCookDurationForm(instance=recipe),
			'nb_pers_form': forms.ChangeNbPersForm(instance=recipe),
			'difficulty_form': forms.ChangeDifficultyForm(instance=recipe),
			'grade_form': forms.ChangeGradeForm(instance=recipe),
			'tag_form': forms.AddTagForm(instance=recipe),
			'ingredient_form': forms.AddIngredientRecipeRelationshipForm(recipe),
			'utensil_form': forms.AddUtensilRecipeRelationshipForm(recipe),
		}
		step_forms = [forms.EditStepForm(instance=step, prefix=f"step_{step.id}") for step in recipe.steps.all()]+[forms.AddStepForm(recipe, prefix="add-step")]
		comments_forms = [forms.EditCommentForm(instance=comment, prefix=f"comment_{comment.id}") for comment in recipe.comments.all()]+[forms.AddCommentForm(recipe, prefix="add-comment")]
		if request.method == "POST":
			forms_dic = {
				'prep_duration_form': forms.ChangePrepDurationForm(request.POST, instance=recipe),
				'cook_duration_form': forms.ChangeCookDurationForm(request.POST, instance=recipe),
				'nb_pers_form': forms.ChangeNbPersForm(request.POST, instance=recipe),
				'difficulty_form': forms.ChangeDifficultyForm(request.POST, instance=recipe),
				'grade_form': forms.ChangeGradeForm(request.POST, instance=recipe),
				'tag_form': forms.AddTagForm(request.POST, instance=recipe),
				'ingredient_form': forms.AddIngredientRecipeRelationshipForm(recipe, request.POST),
				'utensil_form': forms.AddUtensilRecipeRelationshipForm(recipe, request.POST),
			}
			step_forms = [forms.EditStepForm(request.POST, instance=step, prefix=f"step_{step.id}") for step in models.Step.objects.filter(recipe=recipe)]+[forms.AddStepForm(recipe, request.POST, prefix="add-step")]
			comments_forms = [forms.EditCommentForm(request.POST, instance=comment, prefix=f"comment_{comment.id}") for comment in models.Comment.objects.filter(recipe=recipe)]+[forms.AddCommentForm(recipe, request.POST, prefix="add-comment")]
			for form in forms_dic:
				if forms_dic[form].is_valid():
					forms_dic[form].save()
			for form in step_forms+comments_forms:
				if form.is_valid():
					form.save()

			return redirect(f"{reverse('recipe:edit')}?id={recipe_id}")

		helpers.register_view(request, current_page)
		return render(request, "recipe/edit.html", {
			'recipe': recipe,
			**forms_dic,
			'step_forms': step_forms,
			'comments_forms': comments_forms,
		})

	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.change_ingredient')
def update_ingredient(request):
	ingredient_id = request.GET.get('id', False)
	if ingredient_id:
		ingredient = get_object_or_404(models.Ingredient, pk=ingredient_id)
		form = forms.UpdateIngredientForm(instance=ingredient)
		if request.method == "POST":
			form = forms.UpdateIngredientForm(request.POST, request.FILES, instance=ingredient)
			if form.is_valid():
				form.save()
				return redirect(reverse('recipe:create-ingredient'))
		return render(request, "recipe/update/ingredient.html", {'ingredient': ingredient, 'form': form})
	else:
		return redirect(reverse('recipe:create-ingredient'))

@login_required
@permission_required('recipe.change_utensil')
def update_utensil(request):
	utensil_id = request.GET.get('id', False)
	if utensil_id:
		utensil = get_object_or_404(models.Utensil, pk=utensil_id)
		form = forms.UpdateUtensilForm(instance=utensil)
		if request.method == "POST":
			form = forms.UpdateUtensilForm(request.POST, request.FILES, instance=utensil)
			if form.is_valid():
				form.save()
				return redirect(reverse('recipe:create-utensil'))
		return render(request, "recipe/update/utensil.html", {'utensil': utensil, 'form': form})
	else:
		return redirect(reverse('recipe:create-utensil'))


@login_required
@permission_required('recipe.delete_recipeingredientrelationship')
def delete_ingredient_recipe_relationship(request):
	relationship_id = request.GET.get('id', False)
	if relationship_id:
		relationship = get_object_or_404(models.RecipeIngredientRelationship, pk=relationship_id)
		recipe_id = relationship.recipe.id
		relationship.delete()
		return redirect(f"{reverse('recipe:edit')}?id={recipe_id}")
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.change_recipe')
def delete_utensil_recipe_relationship(request):
	utensil_id = request.GET.get('utensil_id', False)
	recipe_id = request.GET.get('recipe_id', False)
	if recipe_id:
		recipe = get_object_or_404(models.Recipe, pk=recipe_id)
		if utensil_id:
			utensil = get_object_or_404(models.Utensil, pk=utensil_id)
			recipe.utensils.remove(utensil)
		return redirect(f"{reverse('recipe:edit')}?id={recipe_id}")
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.delete_step')
def delete_step(request):
	step_id = request.GET.get('id', False)
	if step_id:
		step = get_object_or_404(models.Step, pk=step_id)
		recipe_id = step.recipe.id
		step.delete()
		return redirect(f"{reverse('recipe:edit')}?id={recipe_id}")
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.delete_comment')
def delete_comment(request):
	comment_id = request.GET.get('id', False)
	if comment_id:
		comment = get_object_or_404(models.Comment, pk=comment_id)
		recipe_id = comment.recipe.id
		comment.delete()
		return redirect(f"{reverse('recipe:edit')}?id={recipe_id}")
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.delete_ingredient')
def delete_ingredient(request):
	ingredient_id = request.GET.get('id', False)
	if ingredient_id:
		ingredient = get_object_or_404(models.Ingredient, pk=ingredient_id)
		ingredient.delete()
		return redirect(reverse('recipe:create-ingredient'))
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.delete_utensil')
def delete_utensil(request):
	utensil_id = request.GET.get('id', False)
	if utensil_id:
		utensil = get_object_or_404(models.Utensil, pk=utensil_id)
		utensil.delete()
		return redirect(reverse('recipe:create-utensil'))
	else:
		return redirect(reverse('recipe:list'))

@login_required
@permission_required('recipe.delete_recipe')
def delete_recipe(request):
	recipe_id = request.GET.get('id', False)
	if recipe_id:
		recipe = get_object_or_404(models.Recipe, pk=recipe_id)
		recipe.delete()
	return redirect(reverse('recipe:list'))

def delete_ingredient_from_search(request):
	ingredient_id = int(request.GET.get('id', False))
	if ingredient_id :
		search_recipe = request.session.get('search_recipe', False)
		if search_recipe :
			ingredients = search_recipe.get('ingredients', False)
			if ingredients :
				if ingredient_id in ingredients:
					ingredients.remove(ingredient_id)
				search_recipe.pop('ingredients')
				search_recipe['ingredients'] = ingredients
			request.session.pop('search_recipe')
			request.session['search_recipe'] = search_recipe
	return redirect(reverse('recipe:list'))


def delete_tag_from_search(request):
	tag_id = int(request.GET.get('id', False))
	if tag_id:
		search_recipe = request.session.get('search_recipe', False)
		if search_recipe :
			tags = search_recipe.get('tags', False)
			if tags :
				tags.remove(tag_id)
			search_recipe.pop('tags')
			search_recipe['tags'] = tags
		request.session.pop('search_recipe')
		request.session['search_recipe'] = search_recipe
	return redirect(reverse('recipe:list'))