"""apps/chat/views.py – Vista pagina chat."""
from django.shortcuts import render, get_object_or_404
from apps.tickets.models import Ticket
from .models import Messaggio


def chat_room(request, ticket_id):
    """
    Pagina chat per la vittima (accesso tramite session) o l'operatore (login).
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # Controlla accesso: vittima via sessione o operatore loggato
    session_ticket = request.session.get('ticket_id')
    is_vittima = str(session_ticket) == str(ticket_id)
    is_operatore = request.user.is_authenticated

    if not is_vittima and not is_operatore:
        from django.shortcuts import redirect
        return redirect('core:home')

    messaggi = Messaggio.objects.filter(ticket=ticket).order_by('inviato_il')

    return render(request, 'chat/chat_room.html', {
        'ticket':       ticket,
        'messaggi':     messaggi,
        'is_vittima':   is_vittima,
        'is_operatore': is_operatore,
        'tipo_mittente': 'VITTIMA' if is_vittima else 'OPERATORE',
    })
