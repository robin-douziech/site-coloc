from django.utils.safestring import mark_safe
from django import forms
import django

from . import models

class ImageForm(forms.ModelForm):

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self:
			html_string += "\t<div class=\"field-container\">\n"
			html_string += f"\t\t<p>{field.label} : </p>{field}\n"
			html_string += "\t</div>\n"
		html_string += "\t<input type=\"submit\" value=\"valider\">\n"
		html_string += "</div>\n"
		return mark_safe(html_string)

	def save(self, *args, **kwargs):
		instance = super(ImageForm, self).save(commit=False, *args, **kwargs)
		for field in [f for f in instance._meta.model._meta.fields if f.name!='id']:
			if isinstance(field, django.db.models.FileField):
				setattr(instance, field.name, None)
		instance.save()
		for field in [f for f in instance._meta.model._meta.fields if f.name!='id']:
			if isinstance(field, django.db.models.FileField):
				setattr(instance, field.name, self.cleaned_data[field.name])
		instance.save()
		return instance

	class Meta:
		model = models.ImageModel
		fields = '__all__'