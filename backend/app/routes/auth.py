from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from datetime import timedelta

auth_bp = Blueprint("auth", __name__)

# ---------- REJESTRACJA ----------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    if not data.get("username") or not data.get("password"):
        return jsonify({"msg": "username i password są wymagane"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "użytkownik już istnieje"}), 400

    user = User(username=data["username"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "rejestracja OK"}), 201


# ---------- LOGOWANIE ----------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username")).first()

    if user is None or not user.check_password(data.get("password", "")):
        return jsonify({"msg": "nieprawidłowe dane"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        expires_delta=timedelta(hours=1)
    )
    return jsonify(access_token=access_token), 200


# ---------- ENDPOINT TESTOWY Z JWT ----------
@auth_bp.route("/protected")
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({"msg": f"Jesteś uwierzytelniony, user_id={user_id}"}), 200
