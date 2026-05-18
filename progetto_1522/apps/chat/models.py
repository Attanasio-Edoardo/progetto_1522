"""
apps/chat/models.py

Modello per i messaggi della chat real-time tra vittima e operatore.
"""

from django.db import models
from django.conf import settings
from apps.tickets.models import Ticket


class Messaggio(models.Model):
    """
    Singolo messaggio della chat associato a un ticket.
    Il mittente può essere l'operatore (utente Django) o la vittima (anonima).
    """

    MITTENTE_CHOICES = [
        ('OPERATORE', 'Operatore'),
        ('VITTIMA',   'Vittima'),
    ]

    ticket    = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='messaggi', verbose_name='Ticket'
    )
    operatore = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='messaggi_inviati',
        verbose_name='Operatore mittente'
    )
    tipo_mittente = models.CharField(
        'Tipo mittente', max_length=10,
        choices=MITTENTE_CHOICES
    )
    testo     = models.TextField('Testo messaggio')
    inviato_il = models.DateTimeField('Inviato il', auto_now_add=True)

    class Meta:
        verbose_name = 'Messaggio'
        verbose_name_plural = 'Messaggi'
        ordering = ['inviato_il']

    def __str__(self):
        return f"[{self.inviato_il:%H:%M}] {self.tipo_mittente} → Ticket #{self.ticket_id}"
