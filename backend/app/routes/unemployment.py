from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.unemployment_csv_import import import_unemployment_from_csv

unemployment_bp = Blueprint('unemployment', __name__)

@unemployment_bp.route("/import/csv", methods=["POST"])
@jwt_required()
def import_unemployment_csv():
    """
    POST /api/v1/unemployment/import/csv
    form-data: file=<plik CSV z polskimi nazwami miesięcy>
    """
    if 'file' not in request.files:
        return jsonify({"error": "Brak pliku CSV"}), 400

    file = request.files['file']
    try:
        imported = import_unemployment_from_csv(file.stream, source_id=1)
        return jsonify({"msg": f"Zaimportowano {imported} rekordów"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
