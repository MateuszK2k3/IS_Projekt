# backend/app/routes/unemployment.py
import io
import xml.etree.ElementTree as ET
import json
import yaml
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.region import Region
from app.models.unemployment import Unemployment
from datetime import datetime

unemployment_bp = Blueprint("unemployment", __name__, url_prefix="/api/v1/unemployment")

# mapa nazw miesięcy → numer
MONTHS = {
    "styczeń": 1, "luty": 2, "marzec": 3, "kwiecień": 4,
    "maj": 5, "czerwiec": 6, "lipiec": 7, "sierpień": 8,
    "wrzesień": 9, "październik": 10, "listopad": 11, "grudzień": 12,
}

@unemployment_bp.route("/region-latest")
@jwt_required()
def unemployment_by_region():
    from sqlalchemy import func
    latest_date = db.session.query(func.max(Unemployment.date)).scalar()
    rows = (
        db.session.query(Region.name, Unemployment.rate)
        .join(Unemployment)
        .filter(Unemployment.date == latest_date)
        .all()
    )
    return jsonify([{"region": r[0], "rate": r[1]} for r in rows])

@unemployment_bp.route("/monthly-avg")
@jwt_required()
def unemployment_monthly_avg():
    from sqlalchemy import func
    results = (
        db.session.query(
            func.to_char(Unemployment.date, 'YYYY-MM').label('month'),
            func.avg(Unemployment.rate).label('avg_rate')
        )
        .group_by('month')
        .order_by('month')
        .all()
    )
    return jsonify([{"date": r[0], "rate": round(r[1], 2)} for r in results])

@unemployment_bp.route("/import/file", methods=["POST"])
@jwt_required()
def import_unemployment_file():
    fmt = request.form.get("format", "").lower()
    if fmt not in ("xml", "json", "yaml"):
        return jsonify(error="Format musi być xml, json lub yaml"), 400

    uploaded = request.files.get("file")
    if not uploaded:
        return jsonify(error="Brak pliku"), 400

    content = uploaded.read()
    raw_rows = []

    try:
        if fmt == "xml":
            root = ET.fromstring(content)
            for row in root.findall("row"):
                raw_rows.append({
                    "Kod": row.findtext("Kod", ""),
                    "Nazwa": row.findtext("Nazwa", ""),
                    "Miesiące": row.findtext("Miesiące", ""),
                    "Wskaźniki": row.findtext("Wskaźniki", ""),
                    "Rok": row.findtext("Rok", ""),
                    "Wartosc": row.findtext("Wartosc", "")
                })


        elif fmt == "json":
            data = json.loads(content)
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                if isinstance(data.get("root"), dict) and isinstance(data["root"].get("row"), list):
                    rows = data["root"]["row"]
                elif isinstance(data.get("row"), list):
                    rows = data["row"]
                else:
                    raise ValueError("JSON musi być listą lub zawierać klucz root.row albo row")
            else:
                raise ValueError("Nieobsługiwany format JSON")
            for item in rows:
                raw_rows.append({
                    "Kod": item.get("Kod", ""),
                    "Nazwa": item.get("Nazwa", ""),
                    "Miesiące": item.get("Miesiące", ""),
                    "Wskaźniki": item.get("Wskaźniki", ""),
                    "Rok": item.get("Rok", ""),
                    "Wartosc": item.get("Wartosc", "")

                })

        else:  # yaml
            data = yaml.safe_load(content)
            # dopuszczalne struktury: lista obiektów lub dict z kluczem root.row albo row
            if isinstance(data, list):
                rows = data
            elif isinstance(data, dict):
                if isinstance(data.get("root"), dict) and isinstance(data["root"].get("row"), list):
                    rows = data["root"]["row"]
                elif isinstance(data.get("row"), list):
                    rows = data["row"]
                else:
                    raise ValueError("YAML musi być listą lub zawierać klucz root.row albo row")
            else:
                raise ValueError("Nieobsługiwany format YAML")

            for item in rows:
                raw_rows.append({
                    "Kod": item.get("Kod", ""),
                    "Nazwa": item.get("Nazwa", ""),
                    "Miesiące": item.get("Miesiące", ""),
                    "Wskaźniki": item.get("Wskaźniki", ""),
                    "Rok": item.get("Rok", ""),
                    "Wartosc": item.get("Wartosc", "")
                })

    except Exception as e:
        return jsonify(error=f"Błąd parsowania pliku: {e}"), 400

    # 1) Seed regions
    existing_codes = {r.code for r in Region.query.all()}
    for r in raw_rows:
        code = str(r.get("Kod", "")).strip()
        name = str(r.get("Nazwa", "")).strip()
        if code and name and code not in existing_codes:
            db.session.add(Region(code=code, name=name))
            existing_codes.add(code)
    db.session.flush()  # jeszcze nie commitujemy

    # 2) Seed unemployment
    added = 0
    for r in raw_rows:
        if str(r.get("Wskaźniki", "")).strip() != "stopa bezrobocia rejestrowanego":
            continue

        code   = str(r.get("Kod", "")).strip()
        mon    = str(r.get("Miesiące", "")).strip().lower()
        year_s = str(r.get("Rok", "")).strip()
        rawv   = str(r.get("Wartosc", "")).strip().replace(",", ".")

        if not (code and mon and year_s and rawv):
            continue
        try:
            m    = MONTHS[mon]
            date = datetime(int(year_s), m, 1).date()
            rate = float(rawv)
        except Exception:
            continue

        region = Region.query.filter_by(code=code).first()
        if not region:
            continue
        exists = Unemployment.query.filter_by(region_id=region.id, date=date).first()
        if exists:
            continue

        db.session.add(Unemployment(
            region_id=region.id,
            date=date,
            rate=rate,
            source=f"{fmt}-import"
        ))
        added += 1

    db.session.commit()
    return jsonify(msg=f"Zaimportowano {added} rekordów z pliku"), 200
