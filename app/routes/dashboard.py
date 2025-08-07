from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, crud, auth

router = APIRouter()

@router.get("/", response_model=schemas.DashboardData)
async def get_dashboard(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Les admins n'ont pas de dashboard de congés
    if current_user.role == models.UserRole.ADMIN:
        return schemas.DashboardData(
            remaining_leave_days=0,
            used_leave_days=0,
            total_leave_days=0,
            pending_requests=0,
            approved_requests=0
        )
    
    try:
        dashboard_data = crud.get_dashboard_data(db=db, user_id=current_user.id)
        return dashboard_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/admin/init")
async def initialize_admin(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Endpoint pour créer un administrateur de secours (usage interne uniquement)"""
    # Vérifier si un admin existe déjà
    existing_admin = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Un administrateur existe déjà")
    
    # Créer l'admin de secours
    backup_admin = models.User(
        email="backup@admin.com",
        hashed_password=auth.get_password_hash("backup123"),
        first_name="Backup",
        last_name="Admin",
        role=models.UserRole.ADMIN,
        is_active=True,
        annual_leave_days=25
    )
    
    db.add(backup_admin)
    db.commit()
    db.refresh(backup_admin)
    
    return {"message": "Administrateur de secours créé", "email": "backup@admin.com"}