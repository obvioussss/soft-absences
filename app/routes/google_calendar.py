from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, auth
from app.google_calendar_service import google_calendar_service

router = APIRouter()

@router.get("/status")
async def get_calendar_status(
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Vérifier le statut de l'intégration Google Calendar."""
    return {
        "enabled": google_calendar_service.is_enabled(),
        "calendar_id": google_calendar_service.calendar_id,
        "message": "Service Google Calendar activé" if google_calendar_service.is_enabled() else "Service Google Calendar non configuré"
    }

@router.post("/sync-approved-requests")
async def sync_approved_requests(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Synchroniser toutes les demandes approuvées avec Google Calendar."""
    if not google_calendar_service.is_enabled():
        raise HTTPException(status_code=503, detail="Service Google Calendar non configuré")
    
    # Récupérer toutes les demandes approuvées sans événement Google Calendar
    approved_requests = db.query(models.AbsenceRequest).filter(
        models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE,
        models.AbsenceRequest.google_calendar_event_id.is_(None)
    ).all()
    
    synced_count = 0
    errors = []
    
    for request in approved_requests:
        try:
            event_id = google_calendar_service.create_absence_event(request)
            if event_id:
                request.google_calendar_event_id = event_id
                synced_count += 1
            else:
                errors.append(f"Échec de synchronisation pour la demande {request.id}")
        except Exception as e:
            errors.append(f"Erreur pour la demande {request.id}: {str(e)}")
    
    # Sauvegarder les modifications
    if synced_count > 0:
        db.commit()
    
    return {
        "synced_count": synced_count,
        "total_requests": len(approved_requests),
        "errors": errors,
        "message": f"{synced_count} demandes synchronisées avec Google Calendar"
    }

@router.post("/test-event")
async def create_test_event(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Créer un événement de test dans Google Calendar."""
    if not google_calendar_service.is_enabled():
        raise HTTPException(status_code=503, detail="Service Google Calendar non configuré")
    
    from datetime import date, timedelta
    
    # Créer une vraie demande d'absence pour le test
    test_request = models.AbsenceRequest(
        user_id=current_user.id,
        type=models.AbsenceType.VACANCES,
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=2),
        reason="Test d'intégration Google Calendar",
        status=models.AbsenceStatus.APPROUVE,
        admin_comment="Événement de test créé par l'admin",
        approved_by_id=current_user.id
    )
    
    try:
        event_id = google_calendar_service.create_absence_event(test_request)
        if event_id:
            return {
                "success": True,
                "event_id": event_id,
                "message": "Événement de test créé avec succès",
                "note": "Cet événement peut être supprimé manuellement du calendrier"
            }
        else:
            raise HTTPException(status_code=500, detail="Échec de création de l'événement de test")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'événement de test: {str(e)}")

@router.get("/events")
async def get_calendar_events(
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Récupérer les événements du calendrier Google."""
    if not google_calendar_service.is_enabled():
        raise HTTPException(status_code=503, detail="Service Google Calendar non configuré")
    
    from datetime import datetime, timedelta
    
    # Récupérer les événements des 30 derniers jours et 90 prochains jours
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now() + timedelta(days=90)
    
    try:
        events = google_calendar_service.get_absence_events(start_date, end_date)
        return {
            "events": events,
            "count": len(events),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des événements: {str(e)}")

@router.delete("/orphaned-events")
async def clean_orphaned_events(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Nettoyer les événements Google Calendar orphelins (sans demande d'absence correspondante)."""
    if not google_calendar_service.is_enabled():
        raise HTTPException(status_code=503, detail="Service Google Calendar non configuré")
    
    # Récupérer toutes les demandes avec un event_id Google Calendar
    requests_with_events = db.query(models.AbsenceRequest).filter(
        models.AbsenceRequest.google_calendar_event_id.isnot(None)
    ).all()
    
    # Créer un set des event_ids valides
    valid_event_ids = {req.google_calendar_event_id for req in requests_with_events}
    
    from datetime import datetime, timedelta
    
    # Récupérer tous les événements du calendrier
    start_date = datetime.now() - timedelta(days=365)  # Un an en arrière
    end_date = datetime.now() + timedelta(days=365)    # Un an en avant
    
    try:
        calendar_events = google_calendar_service.get_absence_events(start_date, end_date)
        
        deleted_count = 0
        errors = []
        
        for event in calendar_events:
            event_id = event.get('id')
            if event_id and event_id not in valid_event_ids:
                # Cet événement n'a pas de demande d'absence correspondante
                try:
                    if google_calendar_service.delete_absence_event(event_id):
                        deleted_count += 1
                    else:
                        errors.append(f"Échec de suppression de l'événement {event_id}")
                except Exception as e:
                    errors.append(f"Erreur pour l'événement {event_id}: {str(e)}")
        
        return {
            "deleted_count": deleted_count,
            "total_events": len(calendar_events),
            "errors": errors,
            "message": f"{deleted_count} événements orphelins supprimés"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du nettoyage: {str(e)}")