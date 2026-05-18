"""
apps/tickets/forms.py

Form per l'invio di una richiesta di aiuto da parte della vittima.
"""

from django import forms
from .models import Ticket, Vittima, LogAzione


class RichiestaAiutoForm(forms.Form):
    """
    Form pubblico per inviare una richiesta di aiuto al 1522.
    Nome e cognome sono opzionali per garantire l'anonimato.
    """

    # ── Dati personali (opzionali) ──────────────────────────────────────────
    nome = forms.CharField(
        label='Nome', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Opzionale'})
    )
    cognome = forms.CharField(
        label='Cognome', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Opzionale'})
    )
    contatto = forms.CharField(
        label='Telefono o Email di contatto',
        max_length=200,
        help_text='Verrà cifrato e protetto. Non sarà visibile a nessuno senza autorizzazione.'
    )
    fascia_eta = forms.ChoiceField(
        label='Fascia d\'età',
        choices=Vittima.FASCIA_ETA_CHOICES
    )
    regione = forms.ChoiceField(
        label='Regione di provenienza',
        choices=Vittima.REGIONI_CHOICES
    )

    # ── Dati della richiesta ────────────────────────────────────────────────
    data_invio = forms.DateField(
        label='Data',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    ora_invio = forms.TimeField(
        label='Ora',
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    tipo_violenza = forms.ChoiceField(
        label='Tipo di violenza',
        choices=Ticket.TIPO_VIOLENZA_CHOICES
    )
    descrizione = forms.CharField(
        label='Descrizione della situazione',
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Descrivi la situazione...'}),
        help_text='Tutte le informazioni sono trattate in modo riservato.'
    )
    allegato = forms.FileField(
        label='File allegato (foto, documenti, prove)',
        required=False,
        help_text='Opzionale. Formati accettati: immagini, PDF, documenti.'
    )
    livello_urgenza = forms.ChoiceField(
        label='Livello di urgenza',
        choices=Ticket.URGENZA_CHOICES
    )


class CambiaStatoForm(forms.ModelForm):
    """Form per cambiare lo stato di un ticket (usato dagli operatori)."""

    class Meta:
        model = Ticket
        fields = ['stato']


class LogAzioneForm(forms.ModelForm):
    """Form per aggiungere una nota/log dopo aver gestito un ticket."""

    class Meta:
        model = LogAzione
        fields = ['azione', 'esito', 'note_riservate']
        widgets = {
            'note_riservate': forms.Textarea(attrs={'rows': 4}),
            'esito': forms.TextInput(attrs={'placeholder': 'Breve esito dell\'azione intrapresa'}),
        }
