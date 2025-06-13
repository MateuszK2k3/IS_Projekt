from app import db
from datetime import datetime

class Deaths(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    count = db.Column(db.Integer)
    source = db.Column(db.String(64))
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
