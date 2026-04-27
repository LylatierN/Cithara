from django.shortcuts import render, redirect


def login_page(request):
    # If user already has a session, skip login page
    if request.session.get('_auth_user_id'):
        return redirect('dashboard')
    return render(request, 'user/login.html')


def register_page(request):
    # If user already has a session, skip register page
    if request.session.get('_auth_user_id'):
        return redirect('dashboard')
    return render(request, 'user/register.html')


def dashboard_page(request):
    return render(request, 'song/dashboard.html')
