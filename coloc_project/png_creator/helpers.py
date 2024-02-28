from PIL import Image

def new_pixel(pixel, old_color, new_color):
	match old_color:
		case "red":
			pixel_value = pixel[0]
		case "green":
			pixel_value = pixel[1]
		case "blue":
			pixel_value = pixel[2]
		case "black":
			pixel_value = sum(pixel[:3])//3
		case _ :
			return None
	match new_color:
		case "red":
			return (255, max([pixel_value-100, 0]), max([pixel_value-100, 0]), 255)
		case "green":
			return (max([pixel_value-100, 0]), 175, max([pixel_value-100, 0]), 255)
		case "blue":
			return (max([pixel_value-50, 0]), max([pixel_value-50, 0]), 255, 255)
		case "black":
			return (0, 0, 0, 255)
		case _ :
			return None

def pixelcmp(pixel1, pixel2, threshold=0.5):
	for k in range(3):
		if abs(pixel2[k] - pixel1[k]) > threshold*255 :
			return False
	return True

def _rgba_to_png(image, pen_color_old="blue", pen_color_new="blue"):
	new_image = Image.new("RGBA", image.size, "white")
	length, height = new_image.size
	colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "black": (0, 0, 0)}
	for i in range(length):
		for j in range(height):
			old_pixel = image.getpixel((i, j))
			if pixelcmp(old_pixel, colors[pen_color_old], threshold=0.73) :
				pixel = new_pixel(old_pixel, pen_color_old, pen_color_new)
			else:
				pixel = (255, 255, 255, 0)
			new_image.putpixel((i, j), pixel)
	return new_image

def _rgb_to_png(image, pen_color_old="blue", pen_color_new="blue"):
	return _rgba_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)

def _p_to_png(image, pen_color_old="blue", pen_color_new="blue"):
	new_image = Image.new("RGBA", image.size, "white")
	length, height = new_image.size
	colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "black": (0, 0, 0)}
	palette = image.getpalette()
	for i in range(length):
		for j in range(height):
			old_pixel = tuple(palette[3*image.getpixel((i, j)):3*image.getpixel((i, j))+3])
			if pixelcmp(old_pixel, colors[pen_color_old], threshold=0.73) :
				pixel = new_pixel(old_pixel, pen_color_old, pen_color_new)
			else:
				pixel = (255, 255, 255, 0)
			new_image.putpixel((i, j), pixel)
	return new_image

def _l_to_png(image, pen_color_old="black", pen_color_new="black"):
	new_image = Image.new("RGBA", image.size, "white")
	length, height = new_image.size
	for i in range(length):
		for j in range(height):
			old_pixel = image.getpixel((i, j))
			if old_pixel < 128 :
				pixel = new_pixel((old_pixel, old_pixel, old_pixel), pen_color_old, pen_color_new)
			else:
				pixel = (255, 255, 255, 0)
			new_image.putpixel((i, j), pixel)
	return new_image

def _1_to_png(image, pen_color_old="blue", pen_color_new="blue"):
	return _l_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)

def image_to_png(image_model):

	image = Image.open(image_model.image)
	pen_color_old = image_model.pen_color_old
	pen_color_new = image_model.pen_color_new
	
	print(f"mode: {image.mode}")

	match image.mode:
		case "RGBA":
			image = _rgba_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)
		case "RGB":
			image = _rgb_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)
		case "P":
			image = _p_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)
		case "L":
			image = _l_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)
		case "1":
			image = _1_to_png(image, pen_color_old=pen_color_old, pen_color_new=pen_color_new)
		case _ :
			image = None

	if image is not None:
		image.save(f"{image_model.image.path[::-1].split('/', 1)[1][::-1]}/image.png", format="PNG")
		image_model.image = f"{image_model.image.path[::-1].split('/', 1)[1][::-1]}/image.png"
		image_model.save()
