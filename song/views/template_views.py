from django.shortcuts import render


def generate_page(request):
    return render(request, 'song/generate.html')


def dashboard_page(request):
    return render(request, 'song/dashboard.html')
