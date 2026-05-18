"""apps/tickets/urls.py"""
from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('invia/',             views.invia_richiesta,    name='invia'),
    path('conferma/<int:pk>/', views.conferma_richiesta, name='conferma'),
    path('dashboard/',         views.dashboard_operatore, name='dashboard'),
    path('<int:pk>/',          views.dettaglio_ticket,   name='dettaglio'),
]
