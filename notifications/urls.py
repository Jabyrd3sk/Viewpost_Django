from django.urls import path
from .views import notification_list

app_name = 'notifications'
urlpatterns = [
    path('list/', notification_list, name='list'),
]