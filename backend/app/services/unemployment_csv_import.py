import csv
from datetime import datetime
from io import StringIO

from app import db
from app.models.unemployment import Unemployment

# Mapowanie miesięcy z polskich nazw na numery
MONTH_MAP = {
    "styczeń": "01", "luty": "02", "marzec": "03", "kwiecień": "04",
    "maj": "05", "czerwiec": "06", "lipiec": "07", "sierpień": "08",
    "wrzesień": "09", "październik": "10", "listopad": "11", "grudzień": "12"
}

def import_unemployment_from_csv(file_stream, source_id=1):
    """
    file_stream: plik z CSV otwarty w trybie tekstowym.
    source_id:   ID w tabeli sources, skąd pochodzą dane.
    """
    # Przycisk „Open with…” w Postman/Frontend musi wysyłać form-data 'file'
    text = file_stream.read().decode('utf-8')
    reader = csv.DictReader(StringIO(text), delimiter=';', quotechar='"')
    count = 0

    for row in reader:
        try:
            month_name = row["Miesiące"].strip().lower()
            year = row["Rok"].strip()
            rate_str = row["Wartosc"].strip().replace(",", ".")
            month = MONTH_MAP[month_name]
            date_obj = datetime.strptime(f"{year}-{month}-01", "%Y-%m-%d").date()
            rate = float(rate_str)

            entry = Unemployment(
                source_id=source_id,
                date=date_obj,
                rate=rate
            )
            db.session.add(entry)
            count += 1
        except Exception:
            # pomijamy niepoprawne wiersze
            continue

    db.session.commit()
    return count

def seed_from_file(path="backend/data/unemployment.csv", source_id=1):
    """
    Wersja dla pliku w repo, używana tylko raz do zasiania danych.
    path: ścieżka względna od katalogu projektu.
    source_id: ID źródła w tabeli sources (np. GUS).
    """
    with open(path, "rb") as f:
        return import_unemployment_from_csv(f, source_id=source_id)