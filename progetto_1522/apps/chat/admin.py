"""apps/chat/admin.py"""
from django.contrib import admin
from .models import Messaggio

@admin.register(Messaggio)
class MessaggioAdmin(admin.ModelAdmin):
    list_display  = ('inviato_il', 'ticket', 'tipo_mittente', 'operatore')
    list_filter   = ('tipo_mittente',)
    readonly_fields = ('inviato_il',)
