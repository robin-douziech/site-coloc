from django.db import models
from django.utils.translation import gettext_lazy as _
import shutil

def image_name(instance, filename):
	return f"png_creator/image/{instance.id}/{filename}"

class ImageModel(models.Model):

	def delete(self, *args, **kwargs):
		shutil.rmtree(self.image.path[::-1].split('/', 1)[1][::-1])
		super(ImageModel, self).delete(*args, **kwargs	)

	class Color(models.TextChoices):
		RED   = "red",   _("Red")
		GREEN = "green", _("Green")
		BLUE  = "blue",  _("Blue")
		BLACK = "black", _("Black")

	pen_color_old = models.CharField(
		verbose_name = "Couleur du stylo utilisé sur l'image originale",
		max_length = 5,
		choices = Color,
		default = Color.BLUE
	)

	pen_color_new = models.CharField(
		verbose_name = "Couleur de l'écriture sur la nouvelle image",
		max_length = 5,
		choices = Color,
		default = Color.BLUE
	)

	image = models.ImageField(
		verbose_name = "Image",
		upload_to=image_name,
		blank = True,
		null = True
	)