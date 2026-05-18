"""apps/operatori/urls.py"""
from django.urls import path
from . import views

app_name = 'operatori'

urlpatterns = [
    path('login/',          views.login_operatore,      name='login'),
    path('logout/',         views.logout_operatore,     name='logout'),
    path('registrazione/',  views.registrazione_operatore, name='registrazione'),
    path('dashboard/',      views.admin_registrazioni,  name='admin_registrazioni'),
    path('approva/<int:pk>/', views.approva_operatore,  name='approva'),
]
