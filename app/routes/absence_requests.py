from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud, auth
from app.email_service import email_service
from app.google_calendar_service import google_calendar_service

router = APIRouter()

@router.get("/", response_model=list[schemas.AbsenceRequest])
async def read_absence_requests(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == models.UserRole.ADMIN:
        requests = crud.get_absence_requests(db, skip=skip, limit=limit)
    else:
        requests = crud.get_absence_requests(db, skip=skip, limit=limit, user_id=current_user.id)
    return requests

@router.get("/all", response_model=list[schemas.AbsenceRequest])
async def read_all_absence_requests(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    requests = crud.get_absence_requests(db, skip=skip, limit=limit)
    return requests

@router.get("/pending-count")
async def get_pending_requests_count(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Récupère le nombre de demandes d'absence en attente et de déclarations de maladie non vues pour les administrateurs"""
    # Compter les demandes d'absence en attente
    absence_count = db.query(models.AbsenceRequest).filter(
        models.AbsenceRequest.status == models.AbsenceStatus.EN_ATTENTE
    ).count()
    
    # Compter les déclarations de maladie non vues par l'admin
    sickness_count = db.query(models.SicknessDeclaration).filter(
        models.SicknessDeclaration.viewed_by_admin == False
    ).count()
    
    total_count = absence_count + sickness_count
    return {
        "pending_count": total_count,
        "absence_requests": absence_count,
        "sickness_declarations": sickness_count
    }

@router.post("/", response_model=schemas.AbsenceRequest)
async def create_absence_request(
    request: schemas.AbsenceRequestCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Seuls les utilisateurs normaux peuvent créer des demandes d'absence
    if current_user.role == models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Les administrateurs ne peuvent pas créer de demandes d'absence")
    
    db_request = crud.create_absence_request(db=db, request=request, user_id=current_user.id)
    
    # Créer l'événement dans Google Calendar
    if google_calendar_service.is_configured():
        event_id = google_calendar_service.create_event(db_request)
        if event_id:
            # Mettre à jour la demande avec l'ID de l'événement Google Calendar
            db_request.google_calendar_event_id = event_id
            db.commit()
    
    # Notifier les admins par email
    admin_users = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).all()
    admin_emails = [admin.email for admin in admin_users]
    # Toujours inclure l'adresse hello.obvious@gmail.com
    admin_emails = list({*admin_emails, "hello.obvious@gmail.com"})
    
    user_name = f"{current_user.first_name} {current_user.last_name}"
    email_service.send_absence_request_notification(
        admin_emails=list({*admin_emails}),
        user_name=user_name,
        absence_type=request.type.value,
        start_date=str(request.start_date),
        end_date=str(request.end_date),
        reason=request.reason
    )
    
    return db_request

# Routes admin spécifiques (doivent être déclarées AVANT les routes génériques)
@router.put("/admin/{request_id}", response_model=schemas.AbsenceRequest)
async def admin_update_absence(
    request_id: int,
    request_update: schemas.AdminAbsenceUpdate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Modifier une absence existante (admin): dates, type, raison, statut, commentaire admin"""
    db_request = crud.get_absence_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Appliquer les champs standards (ne pas écraser avec None)
    standard_update = schemas.AbsenceRequestUpdate(
        type=request_update.type if request_update.type is not None else db_request.type,
        start_date=request_update.start_date,
        end_date=request_update.end_date,
        reason=request_update.reason
    )
    updated = crud.update_absence_request(db=db, request_id=request_id, request_update=standard_update)
    
    # Appliquer statut/commentaire si fournis
    if request_update.status is not None or request_update.admin_comment is not None:
        admin_update = schemas.AbsenceRequestAdmin(
            status=request_update.status or updated.status,
            admin_comment=request_update.admin_comment or updated.admin_comment
        )
        updated = crud.update_absence_request_status(db=db, request_id=request_id, admin_update=admin_update, admin_id=current_user.id)
    
    # Mettre à jour l'événement Google Calendar
    if google_calendar_service.is_configured() and updated.google_calendar_event_id:
        google_calendar_service.update_event(updated.google_calendar_event_id, updated)
    elif google_calendar_service.is_configured() and not updated.google_calendar_event_id:
        # Créer l'événement s'il n'existe pas encore
        event_id = google_calendar_service.create_event(updated)
        if event_id:
            updated.google_calendar_event_id = event_id
            db.commit()
    
    return updated

@router.delete("/admin/{request_id}")
async def admin_delete_absence(
    request_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Supprimer une absence (admin)"""
    db_request = crud.get_absence_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Supprimer l'événement Google Calendar s'il existe
    if google_calendar_service.is_configured() and db_request.google_calendar_event_id:
        google_calendar_service.delete_event(db_request.google_calendar_event_id)
    
    crud.delete_absence_request(db=db, request_id=request_id)
    return {"message": "Absence supprimée"}

@router.post("/admin", response_model=schemas.AbsenceRequest)
async def create_admin_absence(
    request: schemas.AdminAbsenceCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Créer une absence pour un utilisateur (admin uniquement)"""
    # Vérifier que l'utilisateur cible existe
    target_user = crud.get_user(db, user_id=request.user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    db_request = crud.create_admin_absence(db=db, request=request, admin_id=current_user.id)
    
    # Créer l'événement dans Google Calendar
    if google_calendar_service.is_configured():
        event_id = google_calendar_service.create_event(db_request)
        if event_id:
            # Mettre à jour la demande avec l'ID de l'événement Google Calendar
            db_request.google_calendar_event_id = event_id
            db.commit()
    
    # Notifier l'utilisateur par email
    user_name = f"{target_user.first_name} {target_user.last_name}"
    admin_name = f"{current_user.first_name} {current_user.last_name}"
    email_service.send_admin_absence_notification(
        user_email=target_user.email,
        user_name=user_name,
        admin_name=admin_name,
        absence_type=request.type.value,
        start_date=str(request.start_date),
        end_date=str(request.end_date),
        reason=request.reason,
        admin_comment=request.admin_comment
    )
    
    return db_request

# Routes avec paramètres spécifiques
@router.put("/{request_id}/status", response_model=schemas.AbsenceRequest)
async def update_absence_request_status(
    request_id: int,
    admin_update: schemas.AbsenceRequestAdmin,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_request = crud.get_absence_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    updated_request = crud.update_absence_request_status(db=db, request_id=request_id, admin_update=admin_update, admin_id=current_user.id)
    
    # Mettre à jour l'événement Google Calendar
    if google_calendar_service.is_configured() and updated_request.google_calendar_event_id:
        google_calendar_service.update_event(updated_request.google_calendar_event_id, updated_request)
    elif google_calendar_service.is_configured() and not updated_request.google_calendar_event_id:
        # Créer l'événement s'il n'existe pas encore
        event_id = google_calendar_service.create_event(updated_request)
        if event_id:
            updated_request.google_calendar_event_id = event_id
            db.commit()
    
    # Notifier l'utilisateur par email
    user_name = f"{db_request.user.first_name} {db_request.user.last_name}"
    email_service.send_absence_status_notification(
        user_email=db_request.user.email,
        user_name=user_name,
        absence_type=db_request.type.value,
        status=admin_update.status.value,
        admin_comment=admin_update.admin_comment
    )
    
    return updated_request

# Routes génériques (doivent être déclarées APRÈS les routes spécifiques)
@router.get("/{request_id}", response_model=schemas.AbsenceRequest)
async def read_absence_request(
    request_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_request = crud.get_absence_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Vérifier que l'utilisateur peut accéder à cette demande
    if current_user.role != models.UserRole.ADMIN and db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return db_request

@router.put("/{request_id}", response_model=schemas.AbsenceRequest)
async def update_absence_request(
    request_id: int,
    request_update: schemas.AbsenceRequestUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_request = crud.get_absence_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Seuls les utilisateurs normaux peuvent modifier leurs demandes
    if current_user.role == models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Les administrateurs ne peuvent pas modifier les demandes d'absence")
    
    # Seul le propriétaire peut modifier sa demande (et seulement si en attente)
    if db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    if db_request.status != models.AbsenceStatus.EN_ATTENTE:
        raise HTTPException(status_code=400, detail="Impossible de modifier une demande déjà traitée")
    
    updated_request = crud.update_absence_request(db=db, request_id=request_id, request_update=request_update)
    
    # Mettre à jour l'événement Google Calendar
    if google_calendar_service.is_configured() and updated_request.google_calendar_event_id:
        google_calendar_service.update_event(updated_request.google_calendar_event_id, updated_request)
    elif google_calendar_service.is_configured() and not updated_request.google_calendar_event_id:
        # Créer l'événement s'il n'existe pas encore
        event_id = google_calendar_service.create_event(updated_request)
        if event_id:
            updated_request.google_calendar_event_id = event_id
            db.commit()
    
    # Notifier les admins de la modification
    admin_users = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).all()
    admin_emails = [admin.email for admin in admin_users]
    
    user_name = f"{current_user.first_name} {current_user.last_name}"
    email_service.send_absence_modification_notification(
        admin_emails=admin_emails,
        user_name=user_name,
        absence_type=updated_request.type.value,
        start_date=str(updated_request.start_date),
        end_date=str(updated_request.end_date),
        reason=updated_request.reason,
        request_id=request_id
    )
    
    return updated_request

@router.delete("/{request_id}")
async def delete_absence_request(
    request_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_request = crud.get_absence_request(db, request_id=request_id)
    if db_request is None:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Seuls les utilisateurs normaux peuvent supprimer leurs propres demandes
    if current_user.role == models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Les administrateurs ne peuvent pas supprimer les demandes d'absence")
    
    # Seul le propriétaire peut supprimer sa demande
    if db_request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Supprimer l'événement Google Calendar s'il existe
    if google_calendar_service.is_configured() and db_request.google_calendar_event_id:
        google_calendar_service.delete_event(db_request.google_calendar_event_id)
    
    # Notifier les admins de la suppression avant de supprimer la demande
    admin_users = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).all()
    admin_emails = [admin.email for admin in admin_users]
    
    user_name = f"{current_user.first_name} {current_user.last_name}"
    email_service.send_absence_deletion_notification(
        admin_emails=admin_emails,
        user_name=user_name,
        absence_type=db_request.type.value,
        start_date=str(db_request.start_date),
        end_date=str(db_request.end_date),
        reason=db_request.reason,
        request_id=request_id
    )
    
    crud.delete_absence_request(db=db, request_id=request_id)
    return {"message": "Demande supprimée"}

