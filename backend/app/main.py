from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, SessionLocal, engine, get_db


def seed(db: Session) -> None:
    """Quelques données de départ pour ne pas avoir un port vide. 🐳"""
    if db.scalar(select(models.Whale).limit(1)) is not None:
        return
    moby = models.Whale(name="Moby Dock", emoji="🐳")
    bluey = models.Whale(name="Bluey", emoji="🐋")
    db.add_all([moby, bluey])
    db.flush()
    db.add_all(
        [
            models.Container(name="web", image="nginx:latest", status="running", whale_id=moby.id),
            models.Container(name="api", image="python:3.12-slim", status="running", whale_id=moby.id),
            models.Container(name="cache", image="redis:7-alpine", status="stopped", whale_id=bluey.id),
        ]
    )
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crée les tables au démarrage (pas d'Alembic pour un TP) et insère le seed.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Moby Dock API", version="1.0.0", lifespan=lifespan)

# CORS large : pratique en dev. En prod c'est Nginx qui proxy /api → pas de CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Santé ----------
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "moby-dock-api"}


# ---------- Whales ----------
@app.get("/api/whales", response_model=list[schemas.WhaleOut])
def list_whales(db: Session = Depends(get_db)):
    return db.scalars(select(models.Whale)).all()


@app.post("/api/whales", response_model=schemas.WhaleOut, status_code=201)
def create_whale(payload: schemas.WhaleCreate, db: Session = Depends(get_db)):
    if db.scalar(select(models.Whale).where(models.Whale.name == payload.name)):
        raise HTTPException(status_code=409, detail="Une baleine porte déjà ce nom")
    whale = models.Whale(**payload.model_dump())
    db.add(whale)
    db.commit()
    db.refresh(whale)
    return whale


@app.delete("/api/whales/{whale_id}", status_code=204)
def delete_whale(whale_id: int, db: Session = Depends(get_db)):
    whale = db.get(models.Whale, whale_id)
    if whale is None:
        raise HTTPException(status_code=404, detail="Baleine introuvable")
    db.delete(whale)  # cascade → supprime ses conteneurs
    db.commit()


# ---------- Containers (CRUD complet) ----------
@app.get("/api/containers", response_model=list[schemas.ContainerOut])
def list_containers(db: Session = Depends(get_db)):
    return db.scalars(select(models.Container)).all()


@app.get("/api/containers/{container_id}", response_model=schemas.ContainerOut)
def get_container(container_id: int, db: Session = Depends(get_db)):
    container = db.get(models.Container, container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")
    return container


@app.post("/api/containers", response_model=schemas.ContainerOut, status_code=201)
def create_container(payload: schemas.ContainerCreate, db: Session = Depends(get_db)):
    if db.get(models.Whale, payload.whale_id) is None:
        raise HTTPException(status_code=400, detail="whale_id inconnu")
    container = models.Container(**payload.model_dump())
    db.add(container)
    db.commit()
    db.refresh(container)
    return container


@app.put("/api/containers/{container_id}", response_model=schemas.ContainerOut)
def update_container(
    container_id: int, payload: schemas.ContainerUpdate, db: Session = Depends(get_db)
):
    container = db.get(models.Container, container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")
    data = payload.model_dump(exclude_unset=True)
    if "whale_id" in data and db.get(models.Whale, data["whale_id"]) is None:
        raise HTTPException(status_code=400, detail="whale_id inconnu")
    for key, value in data.items():
        setattr(container, key, value)
    db.commit()
    db.refresh(container)
    return container


@app.post("/api/containers/{container_id}/restart", response_model=schemas.ContainerOut)
def restart_container(container_id: int, db: Session = Depends(get_db)):
    """Petit clin d'œil Docker : relance un conteneur (status → running)."""
    container = db.get(models.Container, container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")
    container.status = "running"
    db.commit()
    db.refresh(container)
    return container


@app.delete("/api/containers/{container_id}", status_code=204)
def delete_container(container_id: int, db: Session = Depends(get_db)):
    container = db.get(models.Container, container_id)
    if container is None:
        raise HTTPException(status_code=404, detail="Conteneur introuvable")
    db.delete(container)
    db.commit()
