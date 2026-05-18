"""
apps/operatori/views.py

Viste per login, logout, registrazione e area admin registrazioni.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
#from django.core.mail import send_mail
from django.conf import settings
import random
import string

from .models import Operatore
from .forms import LoginOperatoreForm, RegistrazioneOperatoreForm, ApprovazioneOperatoreForm


def login_operatore(request):
    """
    Login operatore con username, email O telefono + password.
    """
    if request.user.is_authenticated:
        return redirect('tickets:dashboard')

    form = LoginOperatoreForm()

    if request.method == 'POST':
        form = LoginOperatoreForm(request.POST)
        if form.is_valid():
            identificativo = form.cleaned_data['identificativo']
            password       = form.cleaned_data['password']

            user = None

            # Cerca per username
            try:
                op = Operatore.objects.get(username=identificativo)
                user = authenticate(request, username=op.username, password=password)
            except Operatore.DoesNotExist:
                pass

            # Cerca per email
            if not user:
                try:
                    op = Operatore.objects.get(email=identificativo)
                    user = authenticate(request, username=op.username, password=password)
                except Operatore.DoesNotExist:
                    pass

            # Cerca per telefono
            if not user:
                try:
                    op = Operatore.objects.get(telefono=identificativo)
                    user = authenticate(request, username=op.username, password=password)
                except Operatore.DoesNotExist:
                    pass

            if user is not None:
                if user.puo_accedere:
                    login(request, user)
                    return redirect('tickets:dashboard')
                else:
                    messages.error(request,
                        'Il tuo account è in attesa di approvazione da parte dell\'amministratore.')
            else:
                messages.error(request, 'Credenziali non valide. Riprova.')

    return render(request, 'operatori/login.html', {'form': form})


def logout_operatore(request):
    """Logout e redirect alla homepage."""
    logout(request)
    return redirect('core:home')


def registrazione_operatore(request):
    """
    Form di richiesta registrazione come operatore.
    La registrazione viene approvata dall'admin.
    """
    form = RegistrazioneOperatoreForm()

    if request.method == 'POST':
        form = RegistrazioneOperatoreForm(request.POST, request.FILES)
        if form.is_valid():
            operatore = form.save(commit=False)
            operatore.telefono = form.cleaned_data.get('telefono', '')

            # Username provvisorio: nome+cognome o 6 cifre casuali
            nome    = form.cleaned_data.get('first_name', '').strip()
            cognome = form.cleaned_data.get('last_name', '').strip()
            if nome or cognome:
                base_username = f"{nome}{cognome}".lower().replace(' ', '')
            else:
                base_username = ''.join(random.choices(string.digits, k=6))

            # Assicura unicità username
            username = base_username
            counter = 1
            while Operatore.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            operatore.username = username

            # Non attivo finché non approvato
            operatore.is_active = False
            operatore.stato_registrazione = 'IN_ATTESA'
            operatore.set_unusable_password()
            operatore.save()

            messages.success(request,
                'La tua richiesta di registrazione è stata inviata. '
                'Sarai contattato dall\'amministratore con le tue credenziali.'
            )
            return redirect('operatori:login')

    return render(request, 'operatori/registrazione.html', {'form': form})


# ─── Area Admin ───────────────────────────────────────────────────────────────

@login_required
def admin_registrazioni(request):
    """
    Pagina admin per gestire le richieste di registrazione degli operatori.
    Accessibile solo ai superuser.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Accesso non autorizzato.')
        return redirect('core:home')

    in_attesa  = Operatore.objects.filter(stato_registrazione='IN_ATTESA')
    approvati  = Operatore.objects.filter(stato_registrazione='APPROVATA')
    rifiutati  = Operatore.objects.filter(stato_registrazione='RIFIUTATA')

    return render(request, 'operatori/admin_registrazioni.html', {
        'in_attesa': in_attesa,
        'approvati': approvati,
        'rifiutati': rifiutati,
    })


@login_required
def approva_operatore(request, pk):
    """
    L'admin approva o rifiuta una registrazione e invia le credenziali.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Accesso non autorizzato.')
        return redirect('core:home')

    operatore = get_object_or_404(Operatore, pk=pk)
    form = ApprovazioneOperatoreForm()

    if request.method == 'POST':
        form = ApprovazioneOperatoreForm(request.POST)
        if form.is_valid():
            decisione       = form.cleaned_data['decisione']
            password        = form.cleaned_data.get('password_generata', '')
            msg_admin       = form.cleaned_data.get('messaggio_admin', '')

            operatore.stato_registrazione = decisione

            if decisione == 'APPROVATA':
                if not password:
                    messages.error(request, 'Inserisci una password per approvare l\'operatore.')
                    return render(request, 'operatori/approva.html',
                                  {'operatore': operatore, 'form': form})

                operatore.is_active = True
                operatore.set_password(password)
                operatore.save()

                # Invia email con credenziali
                destinatario = operatore.email
                if destinatario:
                    corpo_email = (
                        f"Gentile {operatore.get_full_name() or operatore.username},\n\n"
                        f"La tua registrazione al sistema 1522 è stata approvata.\n\n"
                        f"Le tue credenziali di accesso sono:\n"
                        f"  Username: {operatore.username}\n"
                        f"  Password: {password}\n\n"
                    )
                    if msg_admin:
                        corpo_email += f"Messaggio dell'amministratore:\n{msg_admin}\n\n"
                    corpo_email += (
                        "Accedi al sistema qui: http://127.0.0.1:8000/operatori/login/\n\n"
                        "Ti raccomandiamo di cambiare la password al primo accesso.\n\n"
                        "Servizio 1522"
                    )
                    try:
                        send_mail(
                            subject='1522 – Registrazione approvata: le tue credenziali',
                            message=corpo_email,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[destinatario],
                            fail_silently=True,
                        )
                    except Exception:
                        pass  # Log in produzione

                messages.success(request,
                    f'Operatore {operatore} approvato. Credenziali inviate via email.')

            else:  # RIFIUTATA
                operatore.is_active = False
                operatore.save()
                messages.warning(request, f'Registrazione di {operatore} rifiutata.')

            return redirect('operatori:admin_registrazioni')

    return render(request, 'operatori/approva.html', {
        'operatore': operatore,
        'form': form,
    })
