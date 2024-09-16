from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('email_confirmation', views.email_confirmation, name='email_confirmation'),
    path('password_reset', views.password_reset, name='password_reset'),
    path('tracking', views.tracking, name='tracking'),
    path('nutrition', views.nutrition, name='nutrition'),
    path('add_meal', views.add_meal, name='add_meal'),
    path('search', views.search, name='search'),
    path('todays_meals', views.todays_meals, name='todays_meals'),
    path('log_meal/', views.log_meal, name='log_meal'),
    path('delete_meal/<int:meal_id>/', views.delete_meal, name='delete_meal'),
    path('workouts', views.workouts, name='workouts'), 
    path('add_workout/<str:date>', views.add_workout, name='add_workout'),
    path('update_workout/<str:date>', views.update_workout, name='update_workout'),
    path('search_exercise/<str:date>/', views.search_exercise, name='search_exercise'),
    path('add_exercise_to_workout/', views.add_exercise_to_workout, name='add_exercise_to_workout'),
    path('delete_workout/<str:date>/', views.delete_workout, name='delete_workout'),
    path('delete_exercise/<str:date>/', views.delete_exercise, name='delete_exercise'),
    path('log_workout/<str:date>/', views.log_workout, name='log_workout'),
    path('add_custom_meal', views.add_custom_meal, name='add_custom_meal'),
    path('delete_meal/<str:meal_name>/', views.delete_custom_meal, name='delete_custom_meal'),
    path('log_users_meal', views.log_users_meal, name='log_users_meal'),
    path('set_parameters', views.set_parameters, name='set_parameters'),
    path('profile', views.profile, name='profile'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('add_goal', views.add_goal, name='add_goal'),
    path('set_calorie_goal/', views.set_calorie_goal, name='set_calorie_goal'),
    path('about', views.about, name='about'),
    path('contacts', views.contacts, name='contacts'),


]