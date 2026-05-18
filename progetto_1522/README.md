# Progetto 1522 - Sistema Nazionale Anti Violenza e Stalking

Applicazione web Django + PostgreSQL che replica il servizio 1522.

## Requisiti

- Python 3.10+
- PostgreSQL 14+
- pip

## Installazione

### 1. Clona il progetto
```bash
git clone <repo>
cd progetto_1522
```

### 2. Crea e attiva l'ambiente virtuale
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate       # Windows
```

### 3. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configura PostgreSQL
```sql
CREATE DATABASE db_1522;
CREATE USER admin_1522 WITH PASSWORD 'password_sicura_1522';
GRANT ALL PRIVILEGES ON DATABASE db_1522 TO admin_1522;
```

### 5. Configura le variabili d'ambiente
Crea un file `.env` nella root del progetto:
```
SECRET_KEY=cambia_questa_chiave_con_una_molto_lunga_e_casuale
DEBUG=True
DB_NAME=db_1522
DB_USER=admin_1522
DB_PASSWORD=password_sicura_1522
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tua_email@gmail.com
EMAIL_HOST_PASSWORD=tua_app_password
FERNET_KEY=genera_con_python_-c_"from_cryptography.fernet_import_Fernet;print(Fernet.generate_key().decode())"
```

Per generare FERNET_KEY:
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 6. Esegui le migrazioni
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crea il superuser (admin)
```bash
python manage.py createsuperuser
```

### 8. Raccogli i file statici (in produzione)
```bash
python manage.py collectstatic
```

### 9. Avvia il server
```bash
python manage.py runserver
```

Vai su `http://127.0.0.1:8000/`

## Struttura del progetto

```
progetto_1522/
├── config/                  # Configurazione Django (settings, urls, wsgi, asgi)
├── apps/
│   ├── core/                # App principale: homepage, pagine statiche
│   ├── operatori/           # Gestione operatori: registrazione, login, admin
│   ├── tickets/             # Gestione ticket/richieste di aiuto
│   └── chat/                # Chat real-time WebSocket
├── static/                  # File statici (CSS, JS, immagini)
├── templates/               # Template HTML
├── media/                   # File caricati dagli utenti
├── docs/                    # Diagramma E-R e documentazione
├── manage.py
├── requirements.txt
└── README.md
```

## Accesso Admin Django
`http://127.0.0.1:8000/admin/` — con le credenziali del superuser

## Accesso Area Operatori
`http://127.0.0.1:8000/operatori/login/`
