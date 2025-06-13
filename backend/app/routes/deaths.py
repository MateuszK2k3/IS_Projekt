from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.services.eurostat_client import import_deaths_from_eurostat

deaths_bp = Blueprint("deaths", __name__)

@deaths_bp.route("/import", methods=["POST"])
@jwt_required()
def import_deaths():
    try:
        import_deaths_from_eurostat()
        return jsonify({"msg": "Import zakończony"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
