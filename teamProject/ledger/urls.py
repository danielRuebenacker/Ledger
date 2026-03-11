from django.urls import path
from ledger import views

app_name = 'ledger'

urlpatterns = [
    path('', views.index, name='index'),
    path('myhabits', views.myhabits, name='myhabits'),
    path('leaderboards', views.leaderboards, name='leaderboards'),
    path('social', views.social, name='social'),
    path('friends', views.friends, name='friends'),
    path('requests', views.requests_page, name='requests'),
    path('search', views.search_users, name='search'),
    path('nudge', views.nudge_page, name='nudge'),
]