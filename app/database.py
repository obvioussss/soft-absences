from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la base de données selon l'environnement
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "test":
    DATABASE_URL = os.getenv("DATABASE_URL_TEST", "sqlite:///./test_absences.db")
elif ENVIRONMENT == "production":
    # En production sur Vercel, utiliser une base en mémoire
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
else:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./absences.db")

# Configuration pour SQLite
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()