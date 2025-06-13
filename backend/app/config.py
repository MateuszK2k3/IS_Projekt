import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/socialdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET", "secretkey")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "isolation_level": "REPEATABLE READ"
    }
