from django import template

register = template.Library()

@register.filter
def hhmmss_to_mins(value):
	if value.seconds//3600 > 0 :
		if (value.seconds%3600)//60 > 0 :
			return f"{value.seconds//3600}h{f'0{(value.seconds%3600)//60}' if (value.seconds%3600)//60 in range(1,10) else f'{(value.seconds%3600)//60}'}"
		else :
			return f"{value.seconds//3600}h"
	else :
		return f"{value.seconds//60} min"
