from django.urls import path
from . import views

app_name = 'viewpost'
urlpatterns = [
    path('', views.index, name='index'),
    path('feed/', views.post_list, name='post_list'),
    path('new/', views.new_post, name='new_post'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    
    # Comments
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('comment/add/<int:post_id>/', views.comment_page, name='comment_page'),
    path('following/', views.following_feed, name='following'),
    
]