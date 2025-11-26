from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages


class HomePageView(View):
    def get(self, request):
        return render(request, 'app/home_page.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Користувач вже існує!")
            return redirect('register')
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('profile')
    return render(request, 'app/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        messages.error(request, "Невірний логін або пароль!")
        return redirect('login')
    return render(request, 'app/login.html')

def logout_view(request):
    logout(request)
    return redirect('home_page')

@login_required
def profile(request):
    return render(request, 'app/profile.html')