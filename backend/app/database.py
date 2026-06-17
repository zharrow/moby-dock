import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# URL de connexion fournie par docker-compose (service "db").
# Valeur par défaut pratique pour lancer le back en local sans Docker.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://moby:moby@localhost:5432/mobydock",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dépendance FastAPI : ouvre une session par requête puis la ferme."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
