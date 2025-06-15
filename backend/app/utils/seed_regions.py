import os
import xml.etree.ElementTree as ET
from datetime import datetime
from app import db
from app.models.region import Region
from app.models.unemployment import Unemployment

# Mapa PL→numer miesiąca
MONTHS = {
    "styczeń": 1, "luty": 2, "marzec": 3, "kwiecień": 4,
    "maj": 5, "czerwiec": 6, "lipiec": 7, "sierpień": 8,
    "wrzesień": 9, "październik": 10, "listopad": 11, "grudzień": 12,
}

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def seed_regions_from_xml(filename: str = "data.xml") -> int:
    xml_path = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(xml_path):
        raise FileNotFoundError(f"Brak pliku XML do importu: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    existing_codes = {r.code for r in Region.query.all()}
    added = 0

    for row in root.findall("row"):
        code = row.findtext("Kod", "").strip()
        name = row.findtext("Nazwa", "").strip()
        if code and name and code not in existing_codes:
            db.session.add(Region(code=code, name=name))
            existing_codes.add(code)
            added += 1

    db.session.commit()
    return added

def seed_unemployment_from_xml(filename: str = "data.xml") -> int:
    seed_regions_from_xml(filename)
    xml_path = os.path.join(DATA_DIR, filename)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    added = 0
    for row in root.findall("row"):
        if row.findtext("Wskaźniki", "") != "stopa bezrobocia rejestrowanego":
            continue

        code  = row.findtext("Kod", "").strip()
        mon   = row.findtext("Miesiące", "").strip().lower()
        year  = row.findtext("Rok", "").strip()
        raw_v = row.findtext("Wartosc", "").strip().replace(",", ".")

        if not (code and mon and year and raw_v):
            continue

        region = Region.query.filter_by(code=code).first()
        if not region:
            continue

        try:
            month = MONTHS[mon]
            date  = datetime(int(year), month, 1).date()
            rate  = float(raw_v)
        except Exception:
            continue

        exists = Unemployment.query.filter_by(region_id=region.id, date=date).first()
        if exists:
            continue

        db.session.add(Unemployment(
            region_id=region.id,
            date=date,
            rate=rate,
            source="xml-import"
        ))
        added += 1

    db.session.commit()
    return added
