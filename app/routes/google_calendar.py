from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, auth
from app.google_calendar_service import google_calendar_service

router = APIRouter()

@router.get("/status")
async def get_google_calendar_status(
    current_user: models.User = Depends(auth.get_current_admin_user),
):
    """Vérifier le statut de la configuration Google Calendar"""
    is_configured = google_calendar_service.is_configured()
    
    return {
        "configured": is_configured,
        "message": "Google Calendar configuré et prêt" if is_configured else "Google Calendar non configuré"
    }

@router.post("/sync")
async def sync_all_absences(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Synchroniser manuellement toutes les absences avec Google Calendar"""
    if not google_calendar_service.is_configured():
        raise HTTPException(
            status_code=400, 
            detail="Google Calendar n'est pas configuré. Veuillez configurer les variables d'environnement GOOGLE_CALENDAR_CREDENTIALS et GOOGLE_CALENDAR_ID"
        )
    
    try:
        # Synchroniser les demandes d'absence
        absence_requests = db.query(models.AbsenceRequest).filter(
            models.AbsenceRequest.google_calendar_event_id.is_(None)
        ).all()
        
        synced_absences = 0
        failed_absences = 0
        
        for request in absence_requests:
            try:
                event_id = google_calendar_service.create_event(request)
                if event_id:
                    request.google_calendar_event_id = event_id
                    synced_absences += 1
                else:
                    failed_absences += 1
            except Exception as e:
                failed_absences += 1
                print(f"Erreur synchronisation absence {request.id}: {e}")
        
        # Synchroniser les déclarations de maladie
        sickness_declarations = db.query(models.SicknessDeclaration).filter(
            models.SicknessDeclaration.google_calendar_event_id.is_(None)
        ).all()
        
        synced_sickness = 0
        failed_sickness = 0
        
        for declaration in sickness_declarations:
            try:
                event_id = google_calendar_service.create_sickness_event(declaration)
                if event_id:
                    declaration.google_calendar_event_id = event_id
                    synced_sickness += 1
                else:
                    failed_sickness += 1
            except Exception as e:
                failed_sickness += 1
                print(f"Erreur synchronisation déclaration {declaration.id}: {e}")
        
        # Sauvegarder les changements
        db.commit()
        
        return {
            "success": True,
            "message": "Synchronisation terminée",
            "results": {
                "absence_requests": {
                    "total": len(absence_requests),
                    "synced": synced_absences,
                    "failed": failed_absences
                },
                "sickness_declarations": {
                    "total": len(sickness_declarations),
                    "synced": synced_sickness,
                    "failed": failed_sickness
                }
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la synchronisation: {str(e)}")

@router.post("/resync")
async def resync_all_absences(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Re-synchroniser toutes les absences (met à jour les événements existants)"""
    if not google_calendar_service.is_configured():
        raise HTTPException(
            status_code=400, 
            detail="Google Calendar n'est pas configuré"
        )
    
    try:
        # Re-synchroniser les demandes d'absence
        absence_requests = db.query(models.AbsenceRequest).all()
        
        updated_absences = 0
        failed_absences = 0
        
        for request in absence_requests:
            try:
                if request.google_calendar_event_id:
                    # Mettre à jour l'événement existant
                    success = google_calendar_service.update_event(request.google_calendar_event_id, request)
                    if success:
                        updated_absences += 1
                    else:
                        failed_absences += 1
                else:
                    # Créer un nouvel événement
                    event_id = google_calendar_service.create_event(request)
                    if event_id:
                        request.google_calendar_event_id = event_id
                        updated_absences += 1
                    else:
                        failed_absences += 1
            except Exception as e:
                failed_absences += 1
                print(f"Erreur re-synchronisation absence {request.id}: {e}")
        
        # Re-synchroniser les déclarations de maladie
        sickness_declarations = db.query(models.SicknessDeclaration).all()
        
        updated_sickness = 0
        failed_sickness = 0
        
        for declaration in sickness_declarations:
            try:
                if declaration.google_calendar_event_id:
                    # Les déclarations de maladie ne sont pas modifiables, on les recrée si besoin
                    continue
                else:
                    # Créer un nouvel événement
                    event_id = google_calendar_service.create_sickness_event(declaration)
                    if event_id:
                        declaration.google_calendar_event_id = event_id
                        updated_sickness += 1
                    else:
                        failed_sickness += 1
            except Exception as e:
                failed_sickness += 1
                print(f"Erreur re-synchronisation déclaration {declaration.id}: {e}")
        
        # Sauvegarder les changements
        db.commit()
        
        return {
            "success": True,
            "message": "Re-synchronisation terminée",
            "results": {
                "absence_requests": {
                    "total": len(absence_requests),
                    "updated": updated_absences,
                    "failed": failed_absences
                },
                "sickness_declarations": {
                    "total": len(sickness_declarations),
                    "updated": updated_sickness,
                    "failed": failed_sickness
                }
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la re-synchronisation: {str(e)}")