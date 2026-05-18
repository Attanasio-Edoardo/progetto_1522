"""apps/core/urls.py"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',             views.home,       name='home'),
    path('il-1522/',     views.il_1522,    name='il_1522'),
    path('contatti/',    views.contatti,   name='contatti'),
    path('link-utili/',  views.link_utili, name='link_utili'),
    path('mappatura/',   views.mappatura,  name='mappatura'),
]
