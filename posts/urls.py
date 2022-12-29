from django.urls import path
from . import views


app_name = 'travel_posts'

urlpatterns = [
    path('', views.index, name='main'),
    path('follow/', views.follow_index, name='follow_index'),
    path('country/<slug:slug>/', views.country_posts, name='country_posts'),
    path(
        'profile/<str:user_name>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:user_name>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
    path('profile/<str:user_name>/', views.profile, name='profile'),
    path('create/', views.post_create, name='post_create'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.post_like, name='post_like'),
    path('post/<int:post_id>/dislike/', views.post_dislike, name='post_dislike'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
]
