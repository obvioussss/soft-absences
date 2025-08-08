from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud, auth
from app.email_service import email_service

router = APIRouter()

@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")
    created = crud.create_user(db=db, user=user)
    # Notifier l'utilisateur de la création de son compte
    try:
        email_service.send_user_created_notification(
            user_email=created.email,
            user_name=f"{created.first_name} {created.last_name}"
        )
    except Exception:
        # On ne bloque pas la création de compte si l'email échoue
        pass
    return created

@router.get("/", response_model=list[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return db_user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Empêcher l'admin de se modifier lui-même
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, 
            detail="Un administrateur ne peut pas modifier son propre compte"
        )
    
    updated_user = crud.update_user(db=db, user_id=user_id, user_update=user_update)
    try:
        email_service.send_user_updated_notification(
            user_email=updated_user.email,
            user_name=f"{updated_user.first_name} {updated_user.last_name}"
        )
    except Exception:
        pass
    return updated_user

@router.get("/me", response_model=schemas.User)
async def read_current_user(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Obtenir les informations de l'utilisateur connecté"""
    return current_user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    # Empêcher l'admin de se supprimer lui-même
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400, 
            detail="Un administrateur ne peut pas supprimer son propre compte"
        )
    
    success = crud.delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé"}

@router.get("/{user_id}/absence-summary", response_model=schemas.UserAbsenceSummary)
async def get_user_absence_summary(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtenir le résumé des absences d'un utilisateur (admin uniquement)"""
    try:
        summary = crud.get_user_absence_summary(db, user_id=user_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))