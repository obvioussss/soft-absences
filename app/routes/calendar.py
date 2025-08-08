from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract
from datetime import datetime, date
from typing import List, Optional
from calendar import monthrange
import calendar

from app.database import get_db
from app import models, schemas, auth

router = APIRouter()

@router.get("/admin", response_model=List[schemas.CalendarEvent])
async def get_admin_calendar(
    year: int = Query(..., description="Année à afficher"),
    month: int = Query(..., description="Mois à afficher (1-12)"),
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les événements du calendrier pour l'admin (vue mensuelle)
    Affiche toutes les demandes d'absence de tous les utilisateurs
    """
    # Calculer les dates de début et fin du mois
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)
    
    # Récupérer toutes les demandes d'absence du mois
    absence_requests = db.query(models.AbsenceRequest).join(
        models.User, models.AbsenceRequest.user_id == models.User.id
    ).filter(
        and_(
            or_(
                # Demandes qui commencent dans le mois
                and_(
                    models.AbsenceRequest.start_date >= start_date,
                    models.AbsenceRequest.start_date <= end_date
                ),
                # Demandes qui finissent dans le mois
                and_(
                    models.AbsenceRequest.end_date >= start_date,
                    models.AbsenceRequest.end_date <= end_date
                ),
                # Demandes qui couvrent tout le mois
                and_(
                    models.AbsenceRequest.start_date <= start_date,
                    models.AbsenceRequest.end_date >= end_date
                )
            ),
            models.User.is_active == True
        )
    ).all()
    
    # Récupérer aussi les déclarations de maladie du mois
    sickness_declarations = db.query(models.SicknessDeclaration).join(
        models.User, models.SicknessDeclaration.user_id == models.User.id
    ).filter(
        and_(
            or_(
                # Déclarations qui commencent dans le mois
                and_(
                    models.SicknessDeclaration.start_date >= start_date,
                    models.SicknessDeclaration.start_date <= end_date
                ),
                # Déclarations qui finissent dans le mois
                and_(
                    models.SicknessDeclaration.end_date >= start_date,
                    models.SicknessDeclaration.end_date <= end_date
                ),
                # Déclarations qui couvrent tout le mois
                and_(
                    models.SicknessDeclaration.start_date <= start_date,
                    models.SicknessDeclaration.end_date >= end_date
                )
            ),
            models.User.is_active == True
        )
    ).all()
    
    # Convertir en événements calendrier
    calendar_events = []
    
    # Traiter les demandes d'absence
    for request in absence_requests:
        # Créer le titre avec nom de l'utilisateur et type
        type_label = "Vacances" if request.type == models.AbsenceType.VACANCES else "Maladie"
        status_label = ""
        if request.status == models.AbsenceStatus.EN_ATTENTE:
            status_label = " (En attente)"
        elif request.status == models.AbsenceStatus.REFUSE:
            status_label = " (Refusé)"
            
        title = f"{request.user.first_name} {request.user.last_name} - {type_label}{status_label}"
        
        calendar_events.append(schemas.CalendarEvent(
            id=request.id,
            title=title,
            start=max(request.start_date, start_date),  # Ajuster au début du mois si nécessaire
            end=min(request.end_date, end_date),        # Ajuster à la fin du mois si nécessaire
            type=request.type,
            status=request.status,
            user_name=f"{request.user.first_name} {request.user.last_name}",
            reason=request.reason,
            event_source="absence_request"
        ))
    
    # Traiter les déclarations de maladie
    for declaration in sickness_declarations:
        # Créer le titre avec nom de l'utilisateur
        email_status = " ✉️" if declaration.email_sent else " ❌"
        title = f"{declaration.user.first_name} {declaration.user.last_name} - Arrêt maladie{email_status}"
        
        # Les déclarations de maladie sont toujours de type MALADIE et approuvées
        calendar_events.append(schemas.CalendarEvent(
            id=declaration.id,
            title=title,
            start=max(declaration.start_date, start_date),
            end=min(declaration.end_date, end_date),
            type=models.AbsenceType.MALADIE,
            status=models.AbsenceStatus.APPROUVE,  # Les déclarations sont automatiquement approuvées
            user_name=f"{declaration.user.first_name} {declaration.user.last_name}",
            reason=(declaration.pdf_filename or declaration.description),
            event_source="sickness_declaration"
        ))
    
    return calendar_events

@router.get("/user", response_model=List[schemas.CalendarEvent])
async def get_user_calendar(
    year: int = Query(..., description="Année à afficher"),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les événements du calendrier pour un utilisateur (vue annuelle)
    Affiche uniquement ses propres demandes d'absence
    """
    # Calculer les dates de début et fin de l'année
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    # Récupérer les demandes d'absence de l'utilisateur pour l'année
    absence_requests = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == current_user.id,
            or_(
                # Demandes qui commencent dans l'année
                and_(
                    models.AbsenceRequest.start_date >= start_date,
                    models.AbsenceRequest.start_date <= end_date
                ),
                # Demandes qui finissent dans l'année
                and_(
                    models.AbsenceRequest.end_date >= start_date,
                    models.AbsenceRequest.end_date <= end_date
                ),
                # Demandes qui couvrent toute l'année
                and_(
                    models.AbsenceRequest.start_date <= start_date,
                    models.AbsenceRequest.end_date >= end_date
                )
            )
        )
    ).all()
    
    # Récupérer aussi les déclarations de maladie de l'utilisateur
    sickness_declarations = db.query(models.SicknessDeclaration).filter(
        and_(
            models.SicknessDeclaration.user_id == current_user.id,
            or_(
                # Déclarations qui commencent dans l'année
                and_(
                    models.SicknessDeclaration.start_date >= start_date,
                    models.SicknessDeclaration.start_date <= end_date
                ),
                # Déclarations qui finissent dans l'année
                and_(
                    models.SicknessDeclaration.end_date >= start_date,
                    models.SicknessDeclaration.end_date <= end_date
                ),
                # Déclarations qui couvrent toute l'année
                and_(
                    models.SicknessDeclaration.start_date <= start_date,
                    models.SicknessDeclaration.end_date >= end_date
                )
            )
        )
    ).all()
    
    # Convertir en événements calendrier
    calendar_events = []
    
    # Traiter les demandes d'absence
    for request in absence_requests:
        type_label = "Vacances" if request.type == models.AbsenceType.VACANCES else "Maladie"
        status_label = ""
        if request.status == models.AbsenceStatus.EN_ATTENTE:
            status_label = " (En attente)"
        elif request.status == models.AbsenceStatus.REFUSE:
            status_label = " (Refusé)"
            
        title = f"{type_label}{status_label}"
        
        calendar_events.append(schemas.CalendarEvent(
            id=request.id,
            title=title,
            start=max(request.start_date, start_date),
            end=min(request.end_date, end_date),
            type=request.type,
            status=request.status,
            user_name=f"{current_user.first_name} {current_user.last_name}",
            reason=request.reason,
            event_source="absence_request"
        ))
    
    # Traiter les déclarations de maladie
    for declaration in sickness_declarations:
        email_status = " ✉️" if declaration.email_sent else " ❌"
        title = f"Arrêt maladie{email_status}"
        
        calendar_events.append(schemas.CalendarEvent(
            id=declaration.id,
            title=title,
            start=max(declaration.start_date, start_date),
            end=min(declaration.end_date, end_date),
            type=models.AbsenceType.MALADIE,
            status=models.AbsenceStatus.APPROUVE,
            user_name=f"{current_user.first_name} {current_user.last_name}",
            reason=declaration.description,
            event_source="sickness_declaration"
        ))
    
    return calendar_events

@router.get("/summary")
async def get_calendar_summary(
    year: int = Query(..., description="Année pour le résumé"),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère un résumé des congés pour l'année donnée
    """
    # Calculer les jours utilisés dans l'année
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    approved_requests = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == current_user.id,
            models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE,
            models.AbsenceRequest.type == models.AbsenceType.VACANCES,
            models.AbsenceRequest.start_date <= end_date,
            models.AbsenceRequest.end_date >= start_date
        )
    ).all()
    
    # Calculer les jours utilisés
    used_days = 0
    for request in approved_requests:
        # Ajuster les dates pour rester dans l'année
        request_start = max(request.start_date, start_date)
        request_end = min(request.end_date, end_date)
        
        # Calculer le nombre de jours (inclus)
        days_count = (request_end - request_start).days + 1
        used_days += days_count
    
    remaining_days = max(0, current_user.annual_leave_days - used_days)
    
    return {
        "year": year,
        "total_leave_days": current_user.annual_leave_days,
        "used_leave_days": used_days,
        "remaining_leave_days": remaining_days
    }

@router.get("/summary/user/{user_id}")
async def get_calendar_summary_for_user(
    user_id: int,
    year: int = Query(..., description="Année pour le résumé"),
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Résumé des congés pour un utilisateur spécifique (admin)."""
    # Calculer les jours utilisés dans l'année pour l'utilisateur ciblé
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    approved_requests = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == user_id,
            models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE,
            models.AbsenceRequest.type == models.AbsenceType.VACANCES,
            models.AbsenceRequest.start_date <= end_date,
            models.AbsenceRequest.end_date >= start_date
        )
    ).all()

    used_days = 0
    for request in approved_requests:
        request_start = max(request.start_date, start_date)
        request_end = min(request.end_date, end_date)
        days_count = (request_end - request_start).days + 1
        used_days += days_count

    remaining_days = max(0, user.annual_leave_days - used_days)

    return {
        "year": year,
        "total_leave_days": user.annual_leave_days,
        "used_leave_days": used_days,
        "remaining_leave_days": remaining_days
    }