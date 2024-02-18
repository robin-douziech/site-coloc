from django import forms
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
import django, os

from . import models

class MyCreateModelForm(forms.ModelForm):

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self :
			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{field}\n"
			html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)

	def clean(self, *args, **kwargs):
		cleaned_data = super().clean(*args, **kwargs)
		for field_name in self.Meta.unique_fields :
			for instance in self.Meta.model.objects.all():
				instance_field_value = getattr(instance, field_name)
				cleaned_data_value = cleaned_data[field_name]
				if isinstance(instance_field_value, str):
					instance_field_value = instance_field_value.lower()
					cleaned_data_value = cleaned_data[field_name].lower()
				if instance_field_value == cleaned_data_value:
					raise ValidationError(
						_("Invalid value: %(value)s"),
						params={'value': field_name},
						code="invalid"
					)
		return cleaned_data

	def save(self, commit=True, *args, **kwargs):
		instance = super(MyCreateModelForm, self).save(commit=False, *args, **kwargs)
		for field in [f for f in instance._meta.model._meta.fields if f.name!='id']:
			if isinstance(field, django.db.models.FileField):
				setattr(instance, field.name, None)
		instance.save()
		for field in [f for f in instance._meta.model._meta.fields if f.name!='id']:
			if isinstance(field, django.db.models.FileField):
				setattr(instance, field.name, self.cleaned_data[field.name])
		instance.save()
		return instance

class MyEditModelForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(MyEditModelForm, self).__init__(*args, **kwargs)
		self.instance = kwargs['instance']
		self.fields[self.Meta.fields[0]].initial = getattr(self.instance, self.Meta.fields[0])
		self.fields[self.Meta.fields[0]].validators = self.instance._meta.model._meta.get_field(self.Meta.fields[0]).validators
		self.extra_attributs = {}

	def save(self, *args, **kwargs):
		setattr(self.instance, self.Meta.fields[0], self.cleaned_data[self.Meta.fields[0]])
		self.instance.save()
		return self.instance

	def as_p(self):
		html_input = f"<input "
		html_input += f" id=\"id_{self.Meta.fields[0]}\""
		html_input += f" type=\"{self.fields[self.Meta.fields[0]].widget.input_type}\""
		html_input += f" name=\"{self.Meta.fields[0]}\""
		html_input += f" value=\"{self.fields[self.Meta.fields[0]].initial}\""
		for validator in self.fields[self.Meta.fields[0]].validators:
			if isinstance(validator, RegexValidator):
				regex = r"{}".format(validator.regex.pattern)
				html_input += f" pattern=\"{regex}\""
		if isinstance(self.fields[self.Meta.fields[0]], forms.IntegerField):
			for validator in self.fields[self.Meta.fields[0]].validators:
				if isinstance(validator, MinValueValidator):
					html_input += f" min=\"{validator.limit_value}\""
				elif isinstance(validator, MaxValueValidator):
					html_input += f" max=\"{validator.limit_value}\""
		html_input += f"{' required' if self.fields[self.Meta.fields[0]].required else ''}"
		html_input += f"{' disabled' if self.fields[self.Meta.fields[0]].disabled else ''}"
		for extra_attribut in self.extra_attributs :
			html_input += f" {extra_attribut}=\"{self.extra_attributs[extra_attribut]}\""
		html_input += ">"

		html_string = "<div class=\"form-container\">\n"
		html_string += f"\t<div class=\"field-container\">\n"
		html_string += f"\t\t{self.fields[self.Meta.fields[0]].label} : {html_input}<input type=\"submit\" value=\"valider\">\n"
		html_string += f"\t</div>\n"
		html_string += "</div>"

		return mark_safe(html_string)


class CreateRecipeForm(MyCreateModelForm):

	def __init__(self, *args, **kwargs):
		super(CreateRecipeForm, self).__init__(*args, **kwargs)
		self.fields['title'].initial = ""
		self.fields['title'].required = True
		self.fields['prep_duration'].initial = ""
		self.fields['prep_duration'].required = True
		self.fields['cook_duration'].initial = ""
		self.fields['cook_duration'].required = True
		self.fields['image'].required = True

	class Meta:
		model = models.Recipe
		fields = ['title', 'prep_duration', 'cook_duration', 'image']
		unique_fields = ['title']
		widgets = {
			'title': forms.TextInput(attrs={'placeholder': "Titre de la recette"}),
			'prep_duration': forms.TextInput(attrs={'placeholder': "Temps de préparation (hh:mm:ss)"}),
			'cook_duration': forms.TextInput(attrs={'placeholder': "Temps de cuisson (hh:mm:ss)"}),
		}

class CreateIngredientForm(MyCreateModelForm):

	def __init__(self, *args, **kwargs):
		super(CreateIngredientForm, self).__init__(*args, **kwargs)
		self.fields['name'].initial = ""
		self.fields['name'].required = True
		self.fields['image'].required = True

	class Meta:
		model = models.Ingredient
		exclude = []
		unique_fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={'placeholder': "Nom de l'ingrédient"})
		}

class CreateUtensilForm(MyCreateModelForm):

	def __init__(self, *args, **kwargs):
		super(CreateUtensilForm, self).__init__(*args, **kwargs)
		self.fields['name'].initial = ""
		self.fields['name'].required = True
		self.fields['image'].required = True

	class Meta:
		model = models.Utensil
		exclude = []
		unique_fields = ['name']
		widgets = {
			'name': forms.TextInput(attrs={'placeholder': "Nom de l'ustensile"})
		}

class CreateTagForm(MyCreateModelForm):

	def __init__(self, *args, **kwargs):
		super(CreateTagForm, self).__init__(*args, **kwargs)
		self.fields['text'].initial = ""
		self.fields['text'].required = True

	class Meta:
		model = models.Tag
		exclude = []
		unique_fields = ['text']
		widgets = {
			'text': forms.TextInput(attrs={'placeholder': "Texte du tag"})
		}

class ChangePrepDurationForm(MyEditModelForm):

	class Meta:
		model = models.Recipe
		fields = ['prep_duration']

class ChangeCookDurationForm(MyEditModelForm):

	class Meta:
		model = models.Recipe
		fields = ['cook_duration']

class ChangeNbPersForm(MyEditModelForm):

	class Meta:
		model = models.Recipe
		fields = ['nb_pers']

class ChangeDifficultyForm(MyEditModelForm):

	class Meta:
		model = models.Recipe
		fields = ['difficulty']

class ChangeGradeForm(MyEditModelForm):

	class Meta:
		model = models.Recipe
		fields = ['grade']

class AddTagForm(forms.Form):

	def __init__(self, *args, instance, **kwargs):
		super(AddTagForm, self).__init__(*args, **kwargs)
		self.instance = instance
		self.fields['tag_to_add'].queryset = models.Tag.objects.exclude(pk__in=instance.tags.all())
		self.fields['tag_to_del'].queryset = instance.tags.all()

	def as_p(self):
		html_string  = "<div class=\"form-container\">\n"
		html_string += f"\t<div class=\"field-container\">\n"
		html_string += f"\t\tTags : {self['tag_to_add']}<input type=\"submit\" value=\"Ajouter\">{self['tag_to_del']}<input type=\"submit\" value=\"Supprimer\">\n"
		html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)

	def save(self):
		if 'tag_to_add' in self.cleaned_data :
			self.instance.tags.add(self.cleaned_data['tag_to_add'])
		if 'tag_to_del' in self.cleaned_data :
			self.instance.tags.remove(self.cleaned_data['tag_to_del'])
		self.instance.save()
		return self.instance


	tag_to_add = forms.ModelChoiceField(
		label = "Tag to add",
		queryset = None,
		required = False
	)

	tag_to_del = forms.ModelChoiceField(
		label = "Tag to del",
		queryset = None,
		required = False
	)

class AddIngredientRecipeRelationshipForm(forms.ModelForm):
	
	def __init__(self, recipe, *args, **kwargs):
		super(AddIngredientRecipeRelationshipForm, self).__init__(*args, **kwargs)
		self.fields['ingredient'].queryset = models.Ingredient.objects.exclude(pk__in=recipe.ingredients.all())
		self.fields['quantity'].initial = ""
		self.recipe = recipe

	def save(self, *args, **kwargs):
		instance = models.RecipeIngredientRelationship(
			recipe = self.recipe,
			ingredient = self.cleaned_data['ingredient'],
			quantity = self.cleaned_data['quantity']
		)
		instance.save()
		return instance

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self :
			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{self.fields[field.name].label} : {field}\n"
			html_string += f"\t</div>\n"
		html_string += "<input type=\"submit\" value=\"ajouter\">"
		html_string += "</div>"
		return mark_safe(html_string)

	class Meta:
		model = models.RecipeIngredientRelationship
		exclude = ['recipe']

class AddUtensilRecipeRelationshipForm(forms.Form):

	def __init__(self, recipe, *args, **kwargs):
		super(AddUtensilRecipeRelationshipForm, self).__init__(*args, **kwargs)
		self.fields['utensil'].queryset = models.Utensil.objects.exclude(pk__in=recipe.utensils.all())
		self.recipe = recipe

	def save(self):
		self.recipe.utensils.add(self.cleaned_data['utensil'])
		self.recipe.save()

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self :
			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{self.fields[field.name].label} : {field}\n"
			html_string += f"\t</div>\n"
		html_string += "<input type=\"submit\" value=\"ajouter\">"
		html_string += "</div>"
		return mark_safe(html_string)		

	utensil = forms.ModelChoiceField(
		label = "Ustensile",
		queryset = None
	)

class EditStepOrCommentForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(EditStepOrCommentForm, self).__init__(*args, **kwargs)
		self.instance = kwargs['instance']
		self.recipe = self.instance.recipe
		self.fields['text'].initial = self.instance.text

	def save(self, *args, **kwargs):
		self.instance.text = self.cleaned_data['text']
		self.instance.save()

	def as_p(self):
		href = "#"
		if self.Meta.model == models.Step :
			href = f"{reverse('recipe:delete-step')}?id={self.instance.id}"
		elif self.Meta.model == models.Comment :
			href = f"{reverse('recipe:delete-comment')}?id={self.instance.id}"
		html_string  = "<div class=\"form-container\">\n"
		html_string += f"\t<div class=\"field-container\">\n"
		html_string += f"\t\t{self['text']}\n"
		html_string += f"\t</div>\n"
		html_string += f"\t<div class=\"form-btns\">\n"
		html_string += f"\t\t<input type=\"submit\" value=\"enregistrer\">\n"
		html_string += f"\t\t<a class=\"btn btn--red\" href=\"{href}\"><p>supprimer</p></a>\n"
		html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)


class AddStepOrCommentForm(forms.ModelForm):
	
	def __init__(self, recipe, *args, **kwargs):
		super(AddStepOrCommentForm, self).__init__(*args, **kwargs)
		self.recipe = recipe

	def save(self, *args, **kwargs):
		instance = super(AddStepOrCommentForm, self).save(commit=False)
		instance.recipe = self.recipe
		instance.save()
		return instance

	def as_p(self):
		html_string  = "<div class=\"form-container\">\n"
		html_string += f"\t<div class=\"field-container\">\n"
		html_string += f"\t\t{self['text']}\n"
		html_string += f"\t</div>\n"
		html_string += f"\t<div class=\"form-btns\">\n"
		html_string += f"\t\t<input type=\"submit\" value=\"ajouter\">\n"
		html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)

class EditStepForm(EditStepOrCommentForm):

	class Meta:
		model = models.Step
		exclude = ['recipe']
		widgets = {
			'text': forms.Textarea()
		}

class AddStepForm(AddStepOrCommentForm):

	class Meta:
		model = models.Step
		exclude = ['recipe']
		widgets = {
			'text': forms.Textarea()
		}

class EditCommentForm(EditStepOrCommentForm):

	class Meta:
		model = models.Comment
		exclude = ['recipe']
		widgets = {
			'text': forms.Textarea()
		}

class AddCommentForm(AddStepOrCommentForm):

	class Meta:
		model = models.Comment
		exclude = ['recipe']
		widgets = {
			'text': forms.Textarea()
		}

class SearchRecipeForm(forms.Form):
	
	def __init__(self, request, *args, **kwargs):
	    initial = kwargs.pop('initial', {})
	    super(SearchRecipeForm, self).__init__(*args, **kwargs)
	    self.fields['search'].initial = initial.get('search', '')
	    self.fields['max_duration'].initial = initial.get('max_duration', '')

	def save(self, request):
		search_recipe = request.session.get('search_recipe', {
			'search': "",
			'max_duration': "",
			'ingredients': [],
			'tags': []
		})
		search_recipe['search'] = self.cleaned_data['search']
		search_recipe['max_duration'] = self.cleaned_data['max_duration']
		request.session['search_recipe'] = search_recipe

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field_name in self.fields :
			html_input = f"<input "
			html_input += f" id=\"id_{field_name}\""
			html_input += f" type=\"{self.fields[field_name].widget.input_type}\""
			html_input += f" name=\"{field_name}\""
			html_input += f" value=\"{self.fields[field_name].initial}\""
			for validator in self.fields[field_name].validators:
				if isinstance(validator, RegexValidator):
					regex = r"{}".format(validator.regex.pattern)
					html_input += f" pattern=\"{regex}\""
			if isinstance(self.fields[field_name], forms.IntegerField):
				for validator in self.fields[field_name].validators:
					if isinstance(validator, MinValueValidator):
						html_input += f" min=\"{validator.limit_value}\""
					elif isinstance(validator, MaxValueValidator):
						html_input += f" max=\"{validator.limit_value}\""
			for attr in self.fields[field_name].widget.attrs:
				html_input += f" {attr}=\"{self.fields[field_name].widget.attrs[attr]}\""
			html_input += f"{' required' if self.fields[field_name].required else ''}"
			html_input += f"{' disabled' if self.fields[field_name].disabled else ''}"
			html_input += ">"

			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{html_input}\n"
			html_string += f"\t</div>\n"
		html_string += "<input type=\"submit\" value=\"valider\">\n"
		html_string += "</div>"
		return mark_safe(html_string)

	search = forms.CharField(
		label = "Texte de la recherche",
		max_length = 100,
		required = False,
		widget = forms.TextInput(attrs={'placeholder': "Rechercher"})
	)

	max_duration = forms.CharField(
		label = "Durée maximum",
		validators = [RegexValidator(r"^[0-9]{1,2}:[0-5][0-9]:[0-5][0-9]$")],
		required = False,
		widget = forms.TextInput(attrs={'placeholder': "Durée maximale (cuisson comprise)"})
	)