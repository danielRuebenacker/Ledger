from django.urls import path
from ledger import views

app_name = 'ledger'

urlpatterns = [
        path('', views.index, name='index'),
]
