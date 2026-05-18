"""
apps/core/views.py

Viste per le pagine statiche/informative del sito.
"""

from django.shortcuts import render


def home(request):
    """Homepage del sito 1522."""
    return render(request, 'core/home.html')


def il_1522(request):
    """Pagina informativa sul servizio 1522."""
    return render(request, 'core/il_1522.html')


def contatti(request):
    """Pagina contatti."""
    return render(request, 'core/contatti.html')


def link_utili(request):
    """Pagina con link a risorse esterne (ministeri, polizia, ecc.)."""
    link = [
        {
            'titolo': 'Dipartimento per le Pari Opportunità',
            'url': 'https://www.pariopportunita.gov.it',
            'descrizione': 'Il dipartimento del Governo che promuove il 1522.',
            'categoria': 'Governo',
        },
        {
            'titolo': 'Polizia di Stato',
            'url': 'https://www.poliziadistato.it',
            'descrizione': 'Sportello online e informazioni su come denunciare.',
            'categoria': 'Forze dell\'Ordine',
        },
        {
            'titolo': 'Carabinieri',
            'url': 'https://www.carabinieri.it',
            'descrizione': 'Denunce online e sportelli antiviolenza.',
            'categoria': 'Forze dell\'Ordine',
        },
        {
            'titolo': 'Ministero della Giustizia',
            'url': 'https://www.giustizia.it',
            'descrizione': 'Informazioni su tutela legale e procedimenti.',
            'categoria': 'Governo',
        },
        {
            'titolo': 'D.i.Re – Donne in Rete contro la violenza',
            'url': 'https://www.direcontrolaviolenza.it',
            'descrizione': 'Rete nazionale di centri antiviolenza.',
            'categoria': 'Associazioni',
        },
        {
            'titolo': 'WeWorld Onlus',
            'url': 'https://www.weworld.it',
            'descrizione': 'Supporto a donne e bambini in situazioni di vulnerabilità.',
            'categoria': 'Associazioni',
        },
        {
            'titolo': 'Telefono Rosa',
            'url': 'https://www.telefonorosa.it',
            'descrizione': 'Supporto psicologico e legale per donne vittime di violenza.',
            'categoria': 'Associazioni',
        },
        {
            'titolo': 'Croce Rossa Italiana',
            'url': 'https://www.cri.it',
            'descrizione': 'Assistenza e supporto alle persone in difficoltà.',
            'categoria': 'Emergenza',
        },
    ]
    return render(request, 'core/link_utili.html', {'link': link})


def mappatura(request):
    """Pagina con mappa delle sedi 1522 sul territorio."""
    # Sedi di esempio (coordinate reali dei capoluoghi)
    sedi = [
        {'citta': 'Roma',    'lat': 41.9028, 'lng': 12.4964, 'indirizzo': 'Via della Lungara, 19'},
        {'citta': 'Milano',  'lat': 45.4654, 'lng': 9.1866,  'indirizzo': 'Viale Monza, 140'},
        {'citta': 'Napoli',  'lat': 40.8518, 'lng': 14.2681, 'indirizzo': 'Piazza Garibaldi, 32'},
        {'citta': 'Torino',  'lat': 45.0703, 'lng': 7.6869,  'indirizzo': 'Corso Vittorio Emanuele II, 35'},
        {'citta': 'Palermo', 'lat': 38.1157, 'lng': 13.3615, 'indirizzo': 'Via Roma, 104'},
        {'citta': 'Bologna', 'lat': 44.4949, 'lng': 11.3426, 'indirizzo': 'Via dell\'Indipendenza, 2'},
        {'citta': 'Firenze', 'lat': 43.7696, 'lng': 11.2558, 'indirizzo': 'Piazza della Repubblica, 1'},
        {'citta': 'Bari',    'lat': 41.1171, 'lng': 16.8719, 'indirizzo': 'Corso Vittorio Emanuele II, 68'},
        {'citta': 'Venezia', 'lat': 45.4408, 'lng': 12.3155, 'indirizzo': 'Piazzale Roma, 496'},
        {'citta': 'Catania', 'lat': 37.5024, 'lng': 15.0874, 'indirizzo': 'Via Etnea, 210'},
    ]
    return render(request, 'core/mappatura.html', {'sedi': sedi})
