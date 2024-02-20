from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, redirect
from . import models, forms

def login_view(request):
	form = forms.LoginForm()
	if request.method == "POST":
		form = forms.LoginForm(request.POST)
		if form.is_valid():
			user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if user is not None:
				login(request, user)
				return redirect('/coloc/back?nb=1')
	return render(request, "user/login.html", {'form': form})

def logout_view(request):
	logout(request)
	return redirect('/coloc/')

def change_password(request):
	form = forms.ChangePasswordForm(request.user)
	if request.method == "POST":
		form = forms.ChangePasswordForm(request.user, request.POST)
		if form.is_valid():
			request.user.set_password(form.cleaned_data['new_password'])
			request.user.save()
			return redirect('/coloc/back?nb=1')
	return render(request, "user/change-password.html", {'form': form})

@login_required
@permission_required('user.add_user')
def create_user(request):
	form = forms.CreateUserForm()
	if request.method == "POST":
		form = forms.CreateUserForm(request.POST)
		if form.is_valid():
			user = models.User.objects.create_user(
				form.cleaned_data['username'],
				form.cleaned_data['email'],
				form.cleaned_data['password']
			)
			user.save()
			return redirect('/coloc/back?nb=1')
	return render(request, "user/create-user.html", {'form': form})