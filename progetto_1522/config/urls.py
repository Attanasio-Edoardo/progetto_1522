"""
config/urls.py – URL principale del progetto.

NOTA: all'apertura del sito (/) viene mostrato direttamente il form di richiesta aiuto.
La homepage statica è raggiungibile da /home/.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Root "/" → form richiesta di aiuto (come da specifica)
    path('', RedirectView.as_view(url='/tickets/invia/', permanent=False), name='root'),

    # App: core (homepage informativa su /home/, pagine statiche)
    path('home/', include('apps.core.urls')),

    # App: operatori (login, registrazione, dashboard)
    path('operatori/', include('apps.operatori.urls')),

    # App: tickets (invio e gestione richieste)
    path('tickets/', include('apps.tickets.urls')),

    # App: chat (WebSocket e pagina chat)
    path('chat/', include('apps.chat.urls')),
]

# Serve i file media in sviluppo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve i file media in sviluppo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
