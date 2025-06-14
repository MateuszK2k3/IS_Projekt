from app import db
from datetime import datetime

class Unemployment(db.Model):
    __tablename__ = "unemployment"
    id = db.Column(db.Integer, primary_key=True)

    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=False)

    date = db.Column(db.Date, nullable=False)
    rate = db.Column(db.Float)
    source = db.Column(db.String(64))
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    region = db.relationship("Region", back_populates="unemployment")
