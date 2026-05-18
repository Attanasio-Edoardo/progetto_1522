"""
apps/tickets/models.py

Modelli principali del sistema:
- Vittima: chi invia la richiesta di aiuto (dati anonimizzati)
- Ticket: la richiesta di aiuto vera e propria
- LogAzione: traccia ogni azione degli operatori (audit trail GDPR)
"""

from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
import base64


def get_fernet():
    """Restituisce l'istanza Fernet per cifrare/decifrare i contatti."""
    key = getattr(settings, 'FERNET_KEY', None)
    if key:
        return Fernet(key.encode() if isinstance(key, str) else key)
    return None


# ─── Vittima ──────────────────────────────────────────────────────────────────

class Vittima(models.Model):
    """
    Dati della persona che richiede aiuto.
    Nome e cognome sono opzionali per garantire l'anonimato (GDPR).
    Il contatto (telefono/email) viene cifrato con Fernet prima del salvataggio.
    """

    FASCIA_ETA_CHOICES = [
        ('UNDER_18', 'Meno di 18 anni'),
        ('18_25',    '18–25 anni'),
        ('26_35',    '26–35 anni'),
        ('36_45',    '36–45 anni'),
        ('46_60',    '46–60 anni'),
        ('OVER_60',  'Oltre 60 anni'),
        ('ND',       'Preferisco non specificare'),
    ]

    REGIONI_CHOICES = [
        ('ABR', 'Abruzzo'), ('BAS', 'Basilicata'), ('CAL', 'Calabria'),
        ('CAM', 'Campania'), ('EMR', 'Emilia-Romagna'), ('FVG', 'Friuli-Venezia Giulia'),
        ('LAZ', 'Lazio'), ('LIG', 'Liguria'), ('LOM', 'Lombardia'),
        ('MAR', 'Marche'), ('MOL', 'Molise'), ('PIE', 'Piemonte'),
        ('PUG', 'Puglia'), ('SAR', 'Sardegna'), ('SIC', 'Sicilia'),
        ('TOS', 'Toscana'), ('TAA', 'Trentino-Alto Adige'), ('UMB', 'Umbria'),
        ('VDA', 'Valle d\'Aosta'), ('VEN', 'Veneto'), ('ND', 'Non specificata'),
    ]

    # Dati anagrafici (opzionali per anonimato)
    nome    = models.CharField('Nome',    max_length=100, blank=True)
    cognome = models.CharField('Cognome', max_length=100, blank=True)

    # Contatto cifrato: salvato come stringa Base64 della cifratura Fernet
    contatto_cifrato = models.TextField('Contatto cifrato (telefono/email)')

    # Dati statistici
    fascia_eta = models.CharField(
        'Fascia d\'età', max_length=10,
        choices=FASCIA_ETA_CHOICES, default='ND'
    )
    regione = models.CharField(
        'Regione di provenienza', max_length=3,
        choices=REGIONI_CHOICES, default='ND'
    )

    # Timestamp creazione
    creato_il = models.DateTimeField('Creato il', auto_now_add=True)

    def set_contatto(self, valore_in_chiaro: str):
        """Cifra il contatto prima di salvarlo nel DB."""
        f = get_fernet()
        if f:
            self.contatto_cifrato = f.encrypt(valore_in_chiaro.encode()).decode()
        else:
            # Fallback: salva in chiaro se la chiave non è configurata
            self.contatto_cifrato = valore_in_chiaro

    def get_contatto(self) -> str:
        """Decifra e restituisce il contatto. Solo per operatori autorizzati."""
        f = get_fernet()
        if f:
            try:
                return f.decrypt(self.contatto_cifrato.encode()).decode()
            except (InvalidToken, Exception):
                return '[Errore decifratura]'
        return self.contatto_cifrato

    class Meta:
        verbose_name = 'Vittima/Utente'
        verbose_name_plural = 'Vittime/Utenti'

    def __str__(self):
        if self.nome or self.cognome:
            return f"{self.nome} {self.cognome}".strip()
        return f"Utente anonimo #{self.pk}"


# ─── Ticket ───────────────────────────────────────────────────────────────────

class Ticket(models.Model):
    """
    Richiesta di aiuto inviata dalla vittima.
    Tiene traccia di tipo di violenza, urgenza e stato della gestione.
    """

    TIPO_VIOLENZA_CHOICES = [
        ('FISICA',       'Violenza fisica'),
        ('PSICOLOGICA',  'Violenza psicologica'),
        ('STALKING',     'Stalking'),
        ('SESSUALE',     'Violenza sessuale'),
        ('ECONOMICA',    'Violenza economica'),
        ('MISTA',        'Più tipologie'),
    ]

    URGENZA_CHOICES = [
        (1, '1 – Bassa (situazione stabile)'),
        (2, '2 – Media (disagio continuativo)'),
        (3, '3 – Alta (rischio concreto)'),
        (4, '4 – Critica (pericolo imminente)'),
    ]

    STATO_CHOICES = [
        ('APERTA',       'Aperta'),
        ('IN_CARICO',    'In carico'),
        ('CHIUSA',       'Chiusa'),
        ('FALSO_ALLARME','Falso allarme'),
    ]

    # Relazione con la vittima
    vittima = models.ForeignKey(
        Vittima, on_delete=models.PROTECT,
        related_name='tickets', verbose_name='Vittima'
    )

    # Relazione con l'operatore che ha preso in carico (può essere null)
    operatore_assegnato = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tickets_assegnati',
        verbose_name='Operatore assegnato'
    )

    # Dati del ticket
    data_invio   = models.DateField('Data')
    ora_invio    = models.TimeField('Ora')
    tipo_violenza = models.CharField(
        'Tipo di violenza', max_length=20,
        choices=TIPO_VIOLENZA_CHOICES
    )
    descrizione  = models.TextField('Descrizione della situazione')
    livello_urgenza = models.IntegerField(
        'Livello di urgenza', choices=URGENZA_CHOICES, default=2
    )

    # File allegato (opzionale)
    allegato = models.FileField(
        'File allegato (prove/documentazione)',
        upload_to='allegati_tickets/',
        blank=True, null=True
    )

    # Stato del ticket
    stato = models.CharField(
        'Stato', max_length=20,
        choices=STATO_CHOICES, default='APERTA'
    )

    # Timestamp automatici
    creato_il    = models.DateTimeField('Creato il', auto_now_add=True)
    aggiornato_il = models.DateTimeField('Aggiornato il', auto_now=True)

    class Meta:
        verbose_name = 'Ticket / Richiesta'
        verbose_name_plural = 'Ticket / Richieste'
        ordering = ['-livello_urgenza', '-creato_il']

    def __str__(self):
        return f"Ticket #{self.pk} – {self.get_tipo_violenza_display()} (urgenza {self.livello_urgenza})"

    @property
    def is_urgente(self):
        return self.livello_urgenza >= 3


# ─── LogAzione ────────────────────────────────────────────────────────────────

class LogAzione(models.Model):
    """
    Audit trail: registra ogni azione degli operatori su un ticket.
    Fondamentale per la tracciabilità e la conformità GDPR.
    """

    AZIONE_CHOICES = [
        ('PRESO_IN_CARICO',  'Preso in carico'),
        ('CHAT_APERTA',      'Chat aperta con la vittima'),
        ('CHAT_CHIUSA',      'Chat chiusa'),
        ('STATO_CAMBIATO',   'Stato ticket modificato'),
        ('NOTA_AGGIUNTA',    'Nota aggiunta'),
        ('TRASFERITO_112',   'Trasferito al 112'),
        ('TRASFERITO_CAV',   'Indirizzato a Centro Antiviolenza'),
        ('CHIUSO',           'Ticket chiuso'),
    ]

    # Relazioni
    ticket   = models.ForeignKey(
        Ticket, on_delete=models.PROTECT,
        related_name='log_azioni', verbose_name='Ticket'
    )
    operatore = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='log_azioni',
        verbose_name='Operatore'
    )

    # Dettagli dell'azione
    azione  = models.CharField('Azione', max_length=30, choices=AZIONE_CHOICES)
    esito   = models.CharField('Esito', max_length=200, blank=True)
    note_riservate = models.TextField('Note riservate', blank=True)

    # Timestamp automatico
    eseguita_il = models.DateTimeField('Eseguita il', auto_now_add=True)

    class Meta:
        verbose_name = 'Log Azione'
        verbose_name_plural = 'Log Azioni'
        ordering = ['-eseguita_il']

    def __str__(self):
        return f"[{self.eseguita_il:%d/%m/%Y %H:%M}] {self.operatore} – {self.get_azione_display()} su Ticket #{self.ticket_id}"
