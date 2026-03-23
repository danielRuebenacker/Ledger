from django.urls import path
from ledger import views

app_name = 'ledger'

urlpatterns = [
        path('', views.index, name='index'),
        path('myhabits', views.myhabits, name='myhabits'),
        path('leaderboards', views.leaderboards, name='leaderboards'),
        path('social', views.social, name='social'),
        path('profile', views.profile, name='profile'),
        path('settings/',views.settings, name='settings'),
        path('profile/<str:username>/', views.profile, name='profile_user'),
]
