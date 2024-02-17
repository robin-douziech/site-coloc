from django.shortcuts import render, redirect

def index(request):
	return render(request, 'coloc/index.html')

def back(request):
	request.session['previous_pages'] = request.session.get('previous_pages', ['/coloc/'])
	nb_pages = int(request.GET.get('nb', 1))
	if nb_pages == 1:
		if len(request.session['previous_pages']) > 0 :
			print("1")
			return redirect(request.session['previous_pages'].pop())
		else :
			print("2")
			return redirect('/coloc/')
	elif nb_pages == 2:
		if len(request.session['previous_pages']) > 1 :
			request.session['previous_pages'].pop()
			print("3")
			return redirect(request.session['previous_pages'].pop())
		else :
			print("4")
			return redirect('/coloc/')
	else:
		print("5")
		return redirect('/coloc/')