from django.shortcuts import render

@verify_position(['President', 'Adviser'])
def president(request):
    """ Renders the President page and all relevant information """
    return render(request, 'president.html', {})
