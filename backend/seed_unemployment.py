from app import create_app, db
from app.services.unemployment_csv_import import seed_from_file

app = create_app()

with app.app_context():
    print("🔍 Szukam pliku CSV i rozpoczynam import...")
    count = seed_from_file(path="backend/data/unemployment.csv", source_id=1)
    print(f"✅ Zaimportowano {count} rekordów do tabeli unemployment.")
