from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.models.deaths import Deaths
from app.models.unemployment import Unemployment
from app.utils.serializers import serialize_json, serialize_yaml, serialize_xml
from datetime import datetime

export_bp = Blueprint("export", __name__)

@export_bp.route("/export", methods=["GET"])
@jwt_required()
def export_data():
    data_type = request.args.get("type")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    accept = request.headers.get("Accept", "application/json")

    if data_type not in ["deaths", "unemployment"]:
        return {"error": "type musi być 'deaths' lub 'unemployment'"}, 400

    try:
        from_date = datetime.strptime(date_from, "%Y-%m").date()
        to_date = datetime.strptime(date_to, "%Y-%m").date()
    except:
        return {"error": "Niepoprawny format daty. Oczekiwano YYYY-MM."}, 400

    Model = Deaths if data_type == "deaths" else Unemployment
    value_field = "count" if data_type == "deaths" else "rate"

    records = (
        Model.query
        .filter(Model.date >= from_date)
        .filter(Model.date <= to_date)
        .order_by(Model.date)
        .all()
    )

    data = [{"date": r.date.isoformat(), value_field: getattr(r, value_field)} for r in records]

    if accept == "application/xml":
        return serialize_xml(data, value_field=value_field)
    elif accept in ["application/x-yaml", "text/yaml"]:
        return serialize_yaml(data)
    else:
        return serialize_json(data)
