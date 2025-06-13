from flask import Blueprint, jsonify

unemployment_bp = Blueprint('unemployment', __name__)

@unemployment_bp.route("/")
def test_unemployment():
    return jsonify({"message": "Unemployment blueprint działa"})
