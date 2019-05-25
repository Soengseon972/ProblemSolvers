from django.shortcuts import render

# Create your views here.


def index(request):
    context = {}
    return render(request, 'cp1/index.html')