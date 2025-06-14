import os
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.utils.seed_regions import seed_unemployment_from_xml

unemployment_bp = Blueprint("unemployment", __name__, url_prefix="/api/v1/unemployment")

@unemployment_bp.route("/import", methods=["POST"])
@jwt_required()
def import_unemployment():
    count = seed_unemployment_from_xml("data.xml")
    return jsonify({"msg": f"Zaimportowano {count} rekordów bezrobocia"}), 200
