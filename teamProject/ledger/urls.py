from django.urls import path, include
from ledger import views
from registration.backends.simple.views import RegistrationView 
from ledger.forms import CustomRegistrationForm

app_name = 'ledger'

urlpatterns = [
        path('accounts/register/',
                RegistrationView.as_view(
                form_class=CustomRegistrationForm,
                success_url='/'
                ),
                name='registration_register',
        ),
        path('accounts/', include('registration.backends.simple.urls')),
        path('', views.index, name='index'),
        path('myhabits', views.myhabits, name='myhabits'),
        path('leaderboards', views.leaderboards, name='leaderboards'),
        path('social', views.social, name='social'),
        path('profile', views.profile, name='profile'),
        path('api/myhabits/', views.myhabits_api, name='myhabits_api'),
        path('api/create-habit/', views.create_habit_api, name='create_habit_api'),
        path('api/log-habits/', views.log_habits_api, name='log_habits_api'),
        path('settings/',views.settings, name='settings'),
        path('profile/<str:username>/', views.profile, name='profile_user'),
]
