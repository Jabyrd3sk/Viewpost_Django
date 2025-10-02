from django.urls import path, include, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views


app_name = 'accounts'
urlpatterns = [
    # login and logout built-in auth
    path('', include('django.contrib.auth.urls')),
    
    # Registration
    path('register/', views.register, name='register'),
    
    # search user url
    path('search/', views.search_users, name='search_users'),

    # Profile urls
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/toggle_follow/', views.toggle_follow, name='toggle_follow'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),

    # All user profile always the last
    path('profile/<str:username>/', views.view_profile, name='profile'),

    # Settings
    path('settings/', views.settings_page, name='settings'),

    # Change email
    path('email/', views.change_email, name='change_email'),

    # Account deletion
    path('delete/', views.delete_account, name='delete_account'),

 ]