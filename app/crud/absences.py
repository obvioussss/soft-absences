from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime, date
from typing import Optional, List

from app import models, schemas
# Google Calendar supprimé

def get_absence_request(db: Session, request_id: int) -> Optional[models.AbsenceRequest]:
    """Récupérer une demande d'absence par ID"""
    return db.query(models.AbsenceRequest).filter(models.AbsenceRequest.id == request_id).first()

def get_absence_requests(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None, status: Optional[models.AbsenceStatus] = None) -> List[models.AbsenceRequest]:
    """Récupérer les demandes d'absence avec filtres optionnels"""
    # Charger les relations nécessaires pour la sérialisation (évite user=None côté frontend)
    query = db.query(models.AbsenceRequest).options(
        joinedload(models.AbsenceRequest.user),
        joinedload(models.AbsenceRequest.approved_by)
    )
    
    if user_id:
        query = query.filter(models.AbsenceRequest.user_id == user_id)
    if status:
        query = query.filter(models.AbsenceRequest.status == status)
    
    return query.order_by(models.AbsenceRequest.created_at.desc()).offset(skip).limit(limit).all()

def create_absence_request(db: Session, request: schemas.AbsenceRequestCreate, user_id: int) -> models.AbsenceRequest:
    """Créer une nouvelle demande d'absence"""
    db_request = models.AbsenceRequest(
        user_id=user_id,
        type=request.type,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

def create_admin_absence(db: Session, request: schemas.AdminAbsenceCreate, admin_id: int) -> models.AbsenceRequest:
    """Créer une nouvelle absence par un administrateur"""
    db_request = models.AbsenceRequest(
        user_id=request.user_id,
        type=request.type,
        start_date=request.start_date,
        end_date=request.end_date,
        reason=request.reason,
        status=request.status,
        admin_comment=request.admin_comment,
        approved_by_id=admin_id
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Intégration Google Calendar supprimée
    
    return db_request

def update_absence_request(db: Session, request_id: int, request_update: schemas.AbsenceRequestUpdate) -> Optional[models.AbsenceRequest]:
    """Mettre à jour une demande d'absence"""
    db_request = get_absence_request(db, request_id)
    if not db_request:
        return None
    
    update_data = request_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_request, field, value)
    
    # Intégration Google Calendar supprimée
    
    db.commit()
    db.refresh(db_request)
    return db_request

def update_absence_request_status(db: Session, request_id: int, admin_update: schemas.AbsenceRequestAdmin, admin_id: int) -> Optional[models.AbsenceRequest]:
    """Mettre à jour le statut d'une demande d'absence (admin)"""
    db_request = get_absence_request(db, request_id)
    if not db_request:
        return None
    
    old_status = db_request.status
    db_request.status = admin_update.status
    db_request.admin_comment = admin_update.admin_comment
    db_request.approved_by_id = admin_id
    
    # Intégration Google Calendar supprimée
    
    db.commit()
    db.refresh(db_request)
    return db_request

def delete_absence_request(db: Session, request_id: int) -> bool:
    """Supprimer une demande d'absence"""
    db_request = get_absence_request(db, request_id)
    if not db_request:
        return False
    
    # Intégration Google Calendar supprimée
    
    db.delete(db_request)
    db.commit()
    return True

def get_calendar_events(db: Session, start_date: date, end_date: date) -> List[models.AbsenceRequest]:
    """Récupérer les événements pour le calendrier"""
    return db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE,
            or_(
                and_(models.AbsenceRequest.start_date >= start_date, models.AbsenceRequest.start_date <= end_date),
                and_(models.AbsenceRequest.end_date >= start_date, models.AbsenceRequest.end_date <= end_date),
                and_(models.AbsenceRequest.start_date <= start_date, models.AbsenceRequest.end_date >= end_date)
            )
        )
    ).all() 