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
    # En production, prioriser Neon/PostgreSQL puis SQLite fichier
    DATABASE_URL = (
        os.getenv("DATABASE_URL") or
        os.getenv("POSTGRES_URL") or 
        os.getenv("POSTGRES_PRISMA_URL") or
        os.getenv("NEON_DATABASE_URL") or
        "sqlite:////tmp/absences.db"  # Fallback vers /tmp (écriture autorisée sur Vercel)
    )
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