from django.urls import path
from ledger import views

app_name = 'ledger'

urlpatterns = [
        # basic 
        path('', views.index, name='index'),
        path('myhabits/', views.myhabits, name='myhabits'),
        path('leaderboards/', views.leaderboards, name='leaderboards'),
        path('social/', views.social, name='social'),
        path('settings/',views.settings, name='settings'),
        path('profile/', views.profile, name='profile'),
        path('profile/<str:username>/', views.profile, name='profile_user'),

        # apis
        path('api/notifications/get_notifs', views.get_notifications, name='notifications'),
        path('api/notifications/mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
        path('profile/<str:username>/nudge/', views.nudge, name='nudge'),
        path('api/myhabits/', views.myhabits_api, name='myhabits_api'),
        path('api/create_habit/', views.create_habit_api, name='create_habit_api'),
        path('api/log_habits/', views.log_habits_api, name='log_habits_api'),
]
