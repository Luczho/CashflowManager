from django.shortcuts import render


def about(request):
    return render(request, 'costs_records/upgrade-to-pro.html', {'title': 'About'})



# Create your views here.
