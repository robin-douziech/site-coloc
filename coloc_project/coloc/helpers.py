def register_view(request, current_page):
	request.session['previous_pages'] = request.session.get('previous_pages', ['/coloc/'])
	if len(request.session['previous_pages']) == 0 or current_page != request.session['previous_pages'][-1]:
		if len(request.session['previous_pages']) >= 10 :
			request.session['previous_pages'].pop(0)
		request.session['previous_pages'].append(current_page)