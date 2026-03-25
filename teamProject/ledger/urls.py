from django.urls import path
from ledger import views

app_name = 'ledger'

urlpatterns = [
        path('', views.index, name='index'),
        path('myhabits', views.myhabits, name='myhabits'),
        path('leaderboards', views.leaderboards, name='leaderboards'),
        path('social', views.social, name='social'),
        path('profile', views.profile, name='profile'),
        path('api/myhabits/', views.myhabits_api, name='myhabits_api'),
        path('api/create-habit/', views.create_habit_api, name='create_habit_api'),
        path('api/log-habits/', views.log_habits_api, name='log_habits_api'),
]
