### IS Projekt – Analiza danych społecznych (Grupa 07)
Aplikacja webowa służąca do analizy i wizualizacji danych społecznych, takich jak bezrobocie i liczba zgonów w Polsce. Dane importowane są z plików XML lub CSV, przechowywane w bazie PostgreSQL i prezentowane na wykresach w interfejsie graficznym. Projekt korzysta z Dockera i wspiera architekturę mikroserwisów z usługą SOAP.

### Autorzy (Grupa 07)
Mateusz Kozieł

Hubert Kwiatkowski

Yuliia Kozlova

### Struktura katalogów
```
IS_Projekt-feature-gui_docker/
│
├── backend/
│   ├── app/
│   │   ├── models/             # Modele ORM (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── deaths.py
│   │   │   ├── region.py
│   │   │   ├── unemployment.py
│   │   │   ├── user.py
│   │   ├── routes/             # Trasy API i GUI
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── deaths.py
│   │   │   ├── export.py
│   │   │   ├── gui.py
│   │   │   └── unemployment.py
│   │   ├── services/
│   │   │   └── eurostat_client.py
│   │   ├── templates/
│   │   │   └── index.html
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── config.py
│   ├── data/
│   │   └── data.xml            # Przykładowy plik danych
│   ├── migrations/             # Alembic - migracje bazy danych
│   ├── .env
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   └── wsgi.py
│
├── soap_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── soap_server.py
│   └── unemployment.wsdl
│
├── .env
├── docker-compose.yml
├── README.md
└── todo.txt
```


### Technologie
Python 3.11

PostgreSQL (z poziomami izolacji transakcji)

SQLAlchemy (ORM)

Flask (REST API + GUI)

SOAP (serwer usług z plikiem WSDL)

JWT – autoryzacja i uwierzytelnienie

Docker + Docker Compose

### Funkcje
Import danych o bezrobociu i zgonach z plików XML/CSV

Eksport danych do formatu CSV

Interfejs graficzny z wykresami (wykresy liniowe)

REST API z obsługą JSON

Serwis SOAP dla danych o bezrobociu

Logowanie z użyciem tokenów JWT

### Wizualizacje
Wykres bezrobocia w czasie

Wykres liczby zgonów

Możliwość połączenia danych w jednym wykresie

### Uruchomienie aplikacji
W katalogu głównym:

docker-compose up --build

Po uruchomieniu:

## Aplikacja dostępna pod adresem: http://localhost:8000
