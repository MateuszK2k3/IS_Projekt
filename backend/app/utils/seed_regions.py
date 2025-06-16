# backend/app/utils/seed_regions.py
import os
import xml.etree.ElementTree as ET
import json
import yaml
from datetime import datetime
from app import db
from app.models.region import Region
from app.models.unemployment import Unemployment

# Mapa nazw miesięcy → numer
MONTHS = {
    "styczeń":1, "luty":2, "marzec":3, "kwiecień":4,
    "maj":5, "czerwiec":6, "lipiec":7, "sierpień":8,
    "wrzesień":9, "październik":10, "listopad":11, "grudzień":12,
}

# ścieżka do katalogu backend/data
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")

def seed_regions_from_xml(filename="data.xml") -> int:
    xml_path = os.path.join(DATA_DIR, filename)
    if not os.path.isfile(xml_path):
        raise FileNotFoundError(f"Brak pliku XML: {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    existing = {r.code for r in Region.query.all()}
    added = 0
    for row in root.findall("row"):
        code = row.findtext("Kod","").strip()
        name = row.findtext("Nazwa","").strip()
        if code and name and code not in existing:
            db.session.add(Region(code=code, name=name))
            existing.add(code)
            added += 1

    db.session.commit()
    return added

def seed_regions_from_rows(rows: list[dict]) -> int:
    existing = {r.code for r in Region.query.all()}
    added = 0
    for r in rows:
        code = r.get("Kod", "").strip()
        name = r.get("Nazwa", "").strip()
        if code and name and code not in existing:
            db.session.add(Region(code=code, name=name))
            existing.add(code)
            added += 1
    db.session.commit()
    return added


def _parse_rows(rows):
    """
    rows: lista dictów z kluczami jak w XML
    filtruje po 'stopa bezrobocia rejestrowanego',
    zwraca krotki (region_code, date, rate)
    """
    out = []
    for r in rows:
        if r.get("Wskaźniki","") != "stopa bezrobocia rejestrowanego":
            continue
        code = r.get("Kod","").strip()
        mon  = r.get("Miesiące","").strip().lower()
        year = str(r.get("Rok","")).strip()
        raw  = str(r.get("Wartosc","")).replace(",",".").strip()
        if not (code and mon and year and raw):
            continue
        try:
            m    = MONTHS[mon]
            date = datetime(int(year), m, 1).date()
            rate = float(raw)
        except Exception:
            continue
        out.append((code, date, rate))
    return out

def seed_unemployment_from_xml(filename="data.xml") -> int:
    # najpierw regiony
    seed_regions_from_xml(filename)

    xml_path = os.path.join(DATA_DIR, filename)
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # budujemy listę dictów z XML
    rows = []
    for row in root.findall("row"):
        rows.append({
            "Kod":        row.findtext("Kod",""),
            "Wskaźniki":  row.findtext("Wskaźniki",""),
            "Miesiące":   row.findtext("Miesiące",""),
            "Rok":        row.findtext("Rok",""),
            "Wartosc":    row.findtext("Wartosc","")
        })
    records = _parse_rows(rows)

    added = 0
    for code, date, rate in records:
        region = Region.query.filter_by(code=code).first()
        if not region:
            continue
        if Unemployment.query.filter_by(region_id=region.id, date=date).first():
            continue
        db.session.add(Unemployment(region_id=region.id, date=date, rate=rate, source="xml-import"))
        added += 1

    db.session.commit()
    return added

def seed_unemployment_from_json_data(data: dict | list) -> int:
    if isinstance(data, dict) and "root" in data and "row" in data["root"]:
        data = data["root"]["row"]

    if not isinstance(data, list):
        raise ValueError("Oczekiwano listy rekordów w JSON")

    # zapisz regiony z listy
    seed_regions_from_rows(data)

    # przygotuj rekordy do bazy
    rows = []
    for item in data:
        rows.append({
            "Kod":       item.get("Kod", ""),
            "Wskaźniki": item.get("Wskaźniki", ""),
            "Miesiące":  item.get("Miesiące", ""),
            "Rok":       item.get("Rok", ""),
            "Wartosc":   item.get("Wartosc", "")
        })

    records = _parse_rows(rows)

    added = 0
    for code, date, rate in records:
        region = Region.query.filter_by(code=code).first()
        if not region:
            continue
        if Unemployment.query.filter_by(region_id=region.id, date=date).first():
            continue
        db.session.add(Unemployment(region_id=region.id, date=date, rate=rate, source="json-import"))
        added += 1

    db.session.commit()
    return added

def seed_unemployment_from_yaml(filename="data.yaml") -> int:
    # analogicznie do JSON, ale używamy PyYAML
    seed_regions_from_xml("data.yaml")
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("Oczekiwano listy rekordów w YAML")
    rows = []
    for item in data:
        rows.append({
            "Kod":       item.get("Kod",""),
            "Wskaźniki": item.get("Wskaźniki",""),
            "Miesiące":  item.get("Miesiące",""),
            "Rok":       item.get("Rok",""),
            "Wartosc":   item.get("Wartosc","")
        })
    records = _parse_rows(rows)

    added = 0
    for code, date, rate in records:
        region = Region.query.filter_by(code=code).first()
        if not region:
            continue
        if Unemployment.query.filter_by(region_id=region.id, date=date).first():
            continue
        db.session.add(Unemployment(region_id=region.id, date=date, rate=rate, source="yaml-import"))
        added += 1

    db.session.commit()
    return added
