"""
apps/tickets/admin.py

Personalizzazione Django Admin per ticket e log azioni.
I supervisori vedono le statistiche ma NON i dati in chiaro delle vittime
(il contatto rimane cifrato nella lista).
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Vittima, Ticket, LogAzione


@admin.register(Vittima)
class VittimaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nome_anonimizzato', 'fascia_eta', 'regione', 'creato_il')
    list_filter   = ('fascia_eta', 'regione')
    readonly_fields = ('contatto_cifrato', 'creato_il')
    search_fields = ('nome', 'cognome')

    # Nasconde il contatto in chiaro: mostra solo che è cifrato
    def nome_anonimizzato(self, obj):
        if obj.nome or obj.cognome:
            return f"{obj.nome} {obj.cognome}".strip()
        return format_html('<em>Anonimo</em>')
    nome_anonimizzato.short_description = 'Identità'

    # Solo superuser vede il campo contatto_cifrato
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [f for f in fields if f != 'contatto_cifrato']
        return fields


class LogAzioneInline(admin.TabularInline):
    model = LogAzione
    extra = 0
    readonly_fields = ('operatore', 'azione', 'esito', 'eseguita_il')
    can_delete = False


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display   = ('id', 'tipo_violenza', 'urgenza_badge', 'stato', 'operatore_assegnato', 'creato_il')
    list_filter    = ('stato', 'tipo_violenza', 'livello_urgenza')
    search_fields  = ('descrizione',)
    readonly_fields = ('creato_il', 'aggiornato_il')
    inlines        = [LogAzioneInline]

    def urgenza_badge(self, obj):
        colori = {1: 'green', 2: 'orange', 3: 'red', 4: 'darkred'}
        c = colori.get(obj.livello_urgenza, 'gray')
        return format_html(
            '<span style="color:{}; font-weight:bold;">● {}</span>',
            c, obj.get_livello_urgenza_display()
        )
    urgenza_badge.short_description = 'Urgenza'


@admin.register(LogAzione)
class LogAzioneAdmin(admin.ModelAdmin):
    list_display  = ('eseguita_il', 'operatore', 'azione', 'ticket', 'esito')
    list_filter   = ('azione',)
    readonly_fields = ('eseguita_il',)
    search_fields = ('note_riservate', 'esito')
