from app import db
from datetime import datetime

class Unemployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    rate = db.Column(db.Float)
    source = db.Column(db.String(64))
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
