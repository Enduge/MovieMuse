from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_page, name = "register"),
    path('login/', views.login_page, name = "login"),
    path('logout/', views.logout_page, name = "logout"),
    path('profile/', views.profile, name = "profile"),
    path('profile_list/', views.profile_list, name = "profile_list"),
    path('profile_viewer/<str:user>', views.profile_viewer, name = "profile_viewer"),
    path('change_avatar/', views.change_avatar, name = "change_avatar"),
    path('react_to_movie/', views.react_to_movie, name="react_to_movie"),
    path('watchparty/create/', views.create_watch_party, name="watch_party_create"),
    path('watchparty/<int:party_id>/submit/', views.submit_movie_criteria, name="watch_party_submit"),
    path('watchparty/<int:party_id>/choose/', views.choose_movie, name="watch_party_choose"),
    path('watchparty/<int:party_id>/result/', views.watchparty_result, name="watchparty_result"),
]
