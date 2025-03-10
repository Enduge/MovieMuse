from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_page, name = "register"),
    path('login/', views.login_page, name = "login"),
    path('logout/', views.logout_page, name = "logout"),
    path('profile/', views.profile, name = "profile"),
    path('change_avatar/', views.change_avatar, name = "change_avatar"),
    path('react_to_movie/', views.react_to_movie, name="react_to_movie"),
]
