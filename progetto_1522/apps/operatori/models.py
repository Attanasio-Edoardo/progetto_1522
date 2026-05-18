"""
apps/operatori/models.py

Modello Operatore che estende AbstractUser di Django.
Include specializzazione, disponibilità e stato della richiesta di registrazione.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Operatore(AbstractUser):
    """
    Utente operatore del servizio 1522.
    Estende AbstractUser: eredita username, password, email, first_name, last_name.
    """

    SPECIALIZZAZIONE_CHOICES = [
        ('PSICOLOGICA',  'Supporto Psicologico'),
        ('LEGALE',       'Consulenza Legale'),
        ('SOCIALE',      'Assistenza Sociale'),
        ('EMERGENZA',    'Gestione Emergenze'),
        ('GENERALE',     'Operatore Generale'),
    ]

    STATO_REGISTRAZIONE_CHOICES = [
        ('IN_ATTESA',  'In attesa di approvazione'),
        ('APPROVATA',  'Approvata'),
        ('RIFIUTATA',  'Rifiutata'),
    ]

    DISPONIBILITA_CHOICES = [
        ('TURNI_DIURNI',     'Turni diurni'),
        ('TURNI_NOTTURNI',   'Turni notturni'),
        ('TURNI_FESTIVI',    'Turni festivi'),
        ('TURNI_COMPLETI',   'Tutti i turni (H24)'),
    ]

    # Dati di contatto aggiuntivi
    telefono = models.CharField('Numero di telefono', max_length=20, blank=True)

    # Profilo professionale
    specializzazione = models.CharField(
        'Specializzazione',
        max_length=20,
        choices=SPECIALIZZAZIONE_CHOICES,
        default='GENERALE'
    )
    titolo_studio = models.TextField('Titoli di studio e formazione', blank=True)
    curriculum_vitae = models.FileField(
        'Curriculum Vitae (PDF)',
        upload_to='cv_operatori/',
        blank=True,
        null=True
    )
    disponibilita = models.CharField(
        'Disponibilità',
        max_length=20,
        choices=DISPONIBILITA_CHOICES,
        default='TURNI_DIURNI'
    )

    # Stato richiesta di registrazione (gestita dall'admin)
    stato_registrazione = models.CharField(
        'Stato registrazione',
        max_length=20,
        choices=STATO_REGISTRAZIONE_CHOICES,
        default='IN_ATTESA'
    )

    # Flag: solo gli operatori approvati possono fare login
    @property
    def puo_accedere(self):
        return self.stato_registrazione == 'APPROVATA' or self.is_superuser

    class Meta:
        verbose_name = 'Operatore'
        verbose_name_plural = 'Operatori'

    def __str__(self):
        nome = f"{self.first_name} {self.last_name}".strip() or self.username
        return f"{nome} ({self.get_specializzazione_display()})"
