from app import db
from app.models.region import Region

def seed_regions():
    region = Region(name="Polska", code="PL")
    db.session.add(region)
    db.session.commit()

if __name__ == "__main__":
    seed_regions()