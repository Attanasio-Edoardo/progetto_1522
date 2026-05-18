"""
config/asgi.py – Configurazione ASGI per WebSocket (Django Channels).
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importa le URL WebSocket dopo aver impostato l'env
django_asgi_app = get_asgi_application()

from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # Richieste HTTP normali
    'http': django_asgi_app,

    # Connessioni WebSocket con autenticazione
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
