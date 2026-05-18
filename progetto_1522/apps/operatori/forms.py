"""
apps/operatori/forms.py

Form per login, registrazione operatori e approvazione da parte dell'admin.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Operatore


class LoginOperatoreForm(forms.Form):
    """
    Form di login flessibile: accetta username, email o numero di telefono + password.
    """
    identificativo = forms.CharField(
        label='Username, Email o Telefono',
        widget=forms.TextInput(attrs={'placeholder': 'Username, email o numero di telefono'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class RegistrazioneOperatoreForm(forms.ModelForm):
    """
    Form per la richiesta di registrazione come operatore.
    La registrazione viene poi approvata dall'admin.
    """

    # Almeno uno tra email e telefono è obbligatorio: validato in clean()
    email = forms.EmailField(
        label='Email', required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'es. mario.rossi@email.it'})
    )
    telefono = forms.CharField(
        label='Numero di telefono', max_length=20, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'es. +39 333 1234567'})
    )

    class Meta:
        model = Operatore
        fields = [
            'first_name', 'last_name',
            'email', 'telefono',
            'titolo_studio', 'curriculum_vitae', 'disponibilita',
        ]
        labels = {
            'first_name': 'Nome',
            'last_name':  'Cognome',
            'titolo_studio': 'Titoli di studio e formazione specifica',
            'curriculum_vitae': 'Curriculum Vitae (formato europeo, PDF)',
            'disponibilita': 'Disponibilità ai turni',
        }
        widgets = {
            'titolo_studio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Es. Laurea in Psicologia + corso specifico violenza di genere...'
            }),
        }
        help_texts = {
            'titolo_studio': (
                'Indicare: laurea in area socio-psico-educativa (psicologia, sociologia, '
                'servizio sociale, scienze dell\'educazione) o diploma, con formazione '
                'specifica nel contrasto alla violenza di genere.'
            ),
        }

    def clean(self):
        cleaned = super().clean()
        email    = cleaned.get('email')
        telefono = cleaned.get('telefono')
        if not email and not telefono:
            raise forms.ValidationError(
                'È obbligatorio inserire almeno un contatto: email o numero di telefono.'
            )
        return cleaned


class ApprovazioneOperatoreForm(forms.Form):
    """
    Form usato dall'admin per approvare/rifiutare una registrazione
    e inviare le credenziali all'operatore.
    """
    DECISIONE_CHOICES = [
        ('APPROVATA', 'Approva e invia credenziali'),
        ('RIFIUTATA', 'Rifiuta la registrazione'),
    ]

    decisione = forms.ChoiceField(
        label='Decisione', choices=DECISIONE_CHOICES,
        widget=forms.RadioSelect
    )
    password_generata = forms.CharField(
        label='Password da assegnare (solo se approvi)',
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Min. 8 caratteri'}),
        help_text='Lascia vuoto se stai rifiutando la registrazione.'
    )
    messaggio_admin = forms.CharField(
        label='Messaggio per l\'operatore (opzionale)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
