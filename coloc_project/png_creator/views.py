from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import os

from . import models, forms, helpers

def index(request):
	form = forms.ImageForm()
	if request.method == "POST":
		form = forms.ImageForm(request.POST, request.FILES)
		if form.is_valid():
			_image = form.save()
			helpers.image_to_png(_image)
			request.session['image_id'] = _image.id
			return redirect(reverse('png_creator:download-result'))
	return render(request, "png_creator/index.html", {'form': form})

def download_result(request):
	image_id = request.session.get('image_id', False)
	if image_id:
		_image = get_object_or_404(models.ImageModel, pk=image_id)
		response = FileResponse(open(_image.image.path, 'rb'))
		response['Content-Disposition'] = f'attachment; filename="{os.path.basename(_image.image.path)}"'
		_image.delete()
		return response
	else:
		return redirect(reverse('png_creator:index'))