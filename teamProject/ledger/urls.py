from django.urls import path
from ledger import views

app_name = 'ledger'

urlpatterns = [
        path('', views.index, name='index'),
        path('myhabits', views.myhabits, name='myhabits'),
        path('leaderboards', views.leaderboards, name='leaderboards'),
        path('social', views.social, name='social'),
]
