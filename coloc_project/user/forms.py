from django import forms
from django.contrib.auth import authenticate
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from . import models

class LoginForm(forms.Form):

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self :
			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{field}\n"
			html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)

	username = forms.CharField(
		label = "Nom d'utilisateur",
		max_length = 50,
		widget = forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"})
	)

	password = forms.CharField(
		label = "Mot de passe",
		max_length = 50,
		widget = forms.PasswordInput(attrs={'placeholder': "Mot de passe"})
	)

class ChangePasswordForm(forms.Form):

	def __init__(self, request_user, *args, **kwargs):
		super(ChangePasswordForm, self).__init__(*args, **kwargs)
		self.request_user = request_user

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self :
			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{field}\n"
			html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)
	
	old_password = forms.CharField(
		label = "Ancien mot de passe",
		max_length = 50,
		widget = forms.PasswordInput(attrs={'placeholder': "Mot de passe actuel"})
	)

	new_password1 = forms.CharField(
		label = "Nouveau mot de passe",
		max_length = 50,
		widget = forms.PasswordInput(attrs={'placeholder': "Nouveau mot de passe"})
	)

	new_password2 = forms.CharField(
		label = "Confirmez le mot de passe",
		max_length = 50,
		widget = forms.PasswordInput(attrs={'placeholder': "Confirmez le mot de passe"})
	)

	def clean(self):
		old_password = self.cleaned_data['old_password']
		new_password1 = self.cleaned_data['new_password1']
		new_password2 = self.cleaned_data['new_password2']

		if authenticate(username=self.request_user.username, password=old_password) is None :
			raise ValidationError(
				_("Incorrect old password")
			)

		if new_password1 != new_password2 :
			raise ValidationError(
				_("Passwords does not match")
			)

		return self.cleaned_data

class CreateUserForm(forms.Form):

	username = forms.CharField(
		label = "Nom d'utilisateur",
		max_length = 50,
		widget = forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"})
	)

	email = forms.EmailField(
		label = "Email",
		max_length = 50,
		widget = forms.EmailInput(attrs={'placeholder': "e-mail"})
	)

	password = forms.CharField(
		label = "Mot de passe",
		max_length = 50,
		widget = forms.PasswordInput(attrs={'placeholder': "Mot de passe"})
	)

	confirm_password = forms.CharField(
		label = "Mot de passe",
		max_length = 50,
		widget = forms.PasswordInput(attrs={'placeholder': "Confirmez le mot de passe"})
	)

	def as_p(self):
		html_string = "<div class=\"form-container\">\n"
		for field in self :
			html_string += f"\t<div class=\"field-container\">\n"
			html_string += f"\t\t{field}\n"
			html_string += f"\t</div>\n"
		html_string += "</div>"
		return mark_safe(html_string)

	def clean(self):
		username = self.cleaned_data['username']
		email = self.cleaned_data['email']
		password = self.cleaned_data['password']
		confirm_password = self.cleaned_data['confirm_password']

		for user in models.User.objects.all():
			if user.username == username :
				raise ValidationError(
					_("Username already taken : %(username)s"),
					params={'username': username}
				)
			if user.email == email :
				raise ValidationError(
					_("E-mail already taken : %(email)s"),
					params={'email': email}
				)

		if confirm_password != password:
			raise ValidationError(
				_("Passwords does not match")
			)

		return self.cleaned_data

