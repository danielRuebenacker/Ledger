from django.urls import path, include, reverse_lazy
from ledger import views
from registration.backends.simple.views import RegistrationView
from ledger.forms import CustomRegistrationForm

app_name = 'ledger'

urlpatterns = [
        path('accounts/register/',RegistrationView.as_view(form_class=CustomRegistrationForm,success_url=reverse_lazy('ledger:index')),name='registration_register',),
        path('accounts/', include('registration.backends.simple.urls')),
        path('api/friends/request', views.add_friend_request, name='add_friend_request'),
        path('api/friends/handle', views.handle_friend_request, name='handle_friend_request'),
        path('', views.index, name='index'),
        path('myhabits/', views.myhabits, name='myhabits'),
        path('leaderboards/', views.leaderboards, name='leaderboards'),
        path('social/', views.social, name='social'),
        path('profile/', views.profile, name='profile'),
        path('settings/',views.settings, name='settings'),
        path('profile/<str:username>/', views.profile, name='profile_user'),
        path('api/notifications/get_notifs', views.get_notifications, name='notifications'),
        path('api/notifications/mark_read/', views.mark_notifications_read, name='mark_notifications_read'),
        path('profile/<str:username>/nudge/', views.nudge, name='nudge'),
]
