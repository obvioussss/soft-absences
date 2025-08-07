from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.database import engine, get_db
from app.models import Base
from app import models, schemas, crud, auth as app_auth
from app.routes import auth, users, absence_requests, dashboard, calendar, google_calendar, sickness_declarations

# Charger les variables d'environnement
load_dotenv()

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestion des Absences", version="1.0.0")

# Configuration CORS pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "OK", "environment": os.getenv("ENVIRONMENT", "development")}

# Inclure les routes modulaires
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(absence_requests.router, prefix="/absence-requests", tags=["absence-requests"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(google_calendar.router, prefix="/google-calendar", tags=["google-calendar"])
app.include_router(sickness_declarations.router, prefix="/sickness-declarations", tags=["sickness-declarations"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)