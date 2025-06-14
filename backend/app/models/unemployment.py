from app import db
from datetime import datetime

class Unemployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    source_id = db.Column(db.Integer, nullable=False)
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
