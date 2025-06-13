import requests
from app import db
from app.models.deaths import Deaths
from datetime import datetime
from sqlalchemy.exc import IntegrityError

def import_deaths_from_eurostat():
    url = (
        "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
        "demo_r_mweek3?format=JSON&geo=PL&sex=T&age=TOTAL"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Błąd Eurostatu: {response.status_code}")

    data = response.json()
    dataset = data.get("value", {})
    time_keys = data.get("dimension", {}).get("time", {}).get("category", {}).get("index", {})

    if not dataset or not time_keys:
        raise Exception("Brak danych w odpowiedzi Eurostatu")

    # Odwracamy słownik time_keys, by z indeksu uzyskać datę np. "2020-W10"
    reverse_time_keys = {v: k for k, v in time_keys.items()}

    for idx_str, count in dataset.items():
        idx = int(idx_str)
        date_str = reverse_time_keys.get(idx)

        if not date_str or not date_str.startswith("202"):
            continue  # pomijamy dziwne daty

        try:
            # Data w formacie np. "2020-W10"
            iso_date = datetime.strptime(date_str + "-1", "%G-W%V-%u").date()
            record = Deaths(
                date=iso_date,
                count=count,
                source="eurostat",
            )
            db.session.add(record)
        except Exception as e:
            print(f"Błąd przy imporcie rekordu {date_str}: {e}")

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise Exception("Niektóre dane już istnieją w bazie")
