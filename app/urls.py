from django.urls import path
from .views import HomePageView
from . import views
urlpatterns = [
    path('', HomePageView.as_view(), name='home_page'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]