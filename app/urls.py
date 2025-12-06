from django.urls import path
from .views import HomePageView, chat_messages_json, map_view, get_all_locations, update_location
from . import views
urlpatterns = [
    path('home/', HomePageView.as_view(), name='home_page'),
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.user_search, name='user_search'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
    path('chat/<int:chat_id>/json/', chat_messages_json, name='chat_messages_json'),
    path('profile/<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path("map/", map_view, name="map"),
    path("api/map/", get_all_locations),
    path("api/update-location/", update_location),
    path("verify-email/<int:user_id>/", views.verify_email, name="verify_email"),

]