"""
apps/tickets/views.py

Viste per: invio ticket (pubblico), dashboard operatori, gestione ticket.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils import timezone

from .models import Vittima, Ticket, LogAzione
from .forms import RichiestaAiutoForm, CambiaStatoForm, LogAzioneForm


def invia_richiesta(request):
    """
    Vista pubblica: form di invio richiesta di aiuto.
    È la homepage del sito (accessibile senza login).
    """
    if request.method == 'POST':
        form = RichiestaAiutoForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data

            # 1. Crea la vittima con il contatto cifrato
            vittima = Vittima(
                nome=cd.get('nome', ''),
                cognome=cd.get('cognome', ''),
                fascia_eta=cd['fascia_eta'],
                regione=cd['regione'],
            )
            vittima.set_contatto(cd['contatto'])  # cifratura Fernet
            vittima.save()

            # 2. Crea il ticket
            ticket = Ticket.objects.create(
                vittima=vittima,
                data_invio=cd['data_invio'],
                ora_invio=cd['ora_invio'],
                tipo_violenza=cd['tipo_violenza'],
                descrizione=cd['descrizione'],
                livello_urgenza=int(cd['livello_urgenza']),
                allegato=request.FILES.get('allegato'),
                stato='APERTA',
            )

            # Salva in sessione l'ID per la chat (vittima anonima)
            request.session['ticket_id'] = ticket.pk

            messages.success(
                request,
                f'La tua richiesta (#{ticket.pk}) è stata inviata. '
                'Un operatore ti contatterà al più presto. '
                'Puoi seguire la chat aprendo il link ricevuto.'
            )
            return redirect('tickets:conferma', pk=ticket.pk)
    else:
        # Pre-compila data e ora con i valori attuali
        now = timezone.localtime()
        form = RichiestaAiutoForm(initial={
            'data_invio': now.date(),
            'ora_invio':  now.strftime('%H:%M'),
        })

    return render(request, 'tickets/invia_richiesta.html', {'form': form})


def conferma_richiesta(request, pk):
    """Pagina di conferma dopo l'invio del ticket."""
    ticket = get_object_or_404(Ticket, pk=pk)
    return render(request, 'tickets/conferma.html', {'ticket': ticket})


# ─── Area operatori ───────────────────────────────────────────────────────────

@login_required
def dashboard_operatore(request):
    """
    Dashboard: lista di tutti i ticket aperti/in carico.
    I ticket urgenti (urgenza >= 3) sono mostrati per primi.
    """
    # Verifica che l'operatore sia approvato
    if not request.user.puo_accedere:
        messages.error(request, 'Il tuo account è in attesa di approvazione.')
        return redirect('operatori:login')

    tickets_aperti  = Ticket.objects.filter(stato='APERTA').order_by('-livello_urgenza', '-creato_il')
    tickets_in_carico = Ticket.objects.filter(
        stato='IN_CARICO', operatore_assegnato=request.user
    )
    tickets_recenti = Ticket.objects.filter(stato='CHIUSA').order_by('-aggiornato_il')[:10]

    context = {
        'tickets_aperti':    tickets_aperti,
        'tickets_in_carico': tickets_in_carico,
        'tickets_recenti':   tickets_recenti,
    }
    return render(request, 'tickets/dashboard.html', context)


@login_required
def dettaglio_ticket(request, pk):
    """Dettaglio di un ticket: storico log, cambio stato, note."""
    if not request.user.puo_accedere:
        return redirect('operatori:login')

    ticket = get_object_or_404(Ticket, pk=pk)
    log_list = ticket.log_azioni.all()

    form_stato  = CambiaStatoForm(instance=ticket)
    form_log    = LogAzioneForm()

    if request.method == 'POST':
        azione_form = request.POST.get('azione_form')

        # ── Cambia stato ──────────────────────────────────────────────────
        if azione_form == 'cambia_stato':
            form_stato = CambiaStatoForm(request.POST, instance=ticket)
            if form_stato.is_valid():
                vecchio_stato = ticket.stato
                ticket = form_stato.save()
                LogAzione.objects.create(
                    ticket=ticket,
                    operatore=request.user,
                    azione='STATO_CAMBIATO',
                    esito=f'Stato cambiato da {vecchio_stato} a {ticket.stato}',
                )
                messages.success(request, 'Stato aggiornato.')
                return redirect('tickets:dettaglio', pk=pk)

        # ── Prendi in carico ──────────────────────────────────────────────
        elif azione_form == 'prendi_in_carico':
            ticket.stato = 'IN_CARICO'
            ticket.operatore_assegnato = request.user
            ticket.save()
            LogAzione.objects.create(
                ticket=ticket,
                operatore=request.user,
                azione='PRESO_IN_CARICO',
                esito=f'Ticket preso in carico da {request.user}',
            )
            messages.success(request, 'Hai preso in carico il ticket. Puoi avviare la chat.')
            return redirect('tickets:dettaglio', pk=pk)

        # ── Aggiungi nota/log ─────────────────────────────────────────────
        elif azione_form == 'aggiungi_log':
            form_log = LogAzioneForm(request.POST)
            if form_log.is_valid():
                log = form_log.save(commit=False)
                log.ticket   = ticket
                log.operatore = request.user
                log.save()
                messages.success(request, 'Nota salvata nel log.')
                return redirect('tickets:dettaglio', pk=pk)

    context = {
        'ticket':     ticket,
        'log_list':   log_list,
        'form_stato': form_stato,
        'form_log':   form_log,
        # Decifra il contatto solo per l'operatore assegnato o superuser
        'contatto':   ticket.vittima.get_contatto() if (
            request.user.is_superuser or
            ticket.operatore_assegnato == request.user
        ) else None,
    }
    return render(request, 'tickets/dettaglio.html', context)
