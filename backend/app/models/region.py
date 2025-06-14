from app import db

class Region(db.Model):
    __tablename__ = "regions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    code = db.Column(db.String(16), unique=True, nullable=False)

    # relacja do bezrobocia
    unemployment = db.relationship(
        "Unemployment",
        back_populates="region",
        cascade="all, delete-orphan"
    )
