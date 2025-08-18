from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date, timedelta
from typing import Optional

from app import models, schemas
from .users import get_user

def calculate_business_days(start_date: date, end_date: date) -> int:
    """Calculer le nombre de jours ouvrés entre deux dates (inclus)"""
    if start_date > end_date:
        return 0
    
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # 0 = Monday, 6 = Sunday
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days

def calculate_used_leave_days(db: Session, user_id: int, year: int = None) -> int:
    """Calculer le nombre de jours de congés utilisés pour un utilisateur"""
    if year is None:
        year = datetime.now().year
    
    # Période de congés: du 1er juin au 31 mai de l'année suivante
    start_period = date(year, 6, 1)
    end_period = date(year + 1, 5, 31)
    
    approved_requests = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == user_id,
            models.AbsenceRequest.type == models.AbsenceType.VACANCES,
            models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE,
            models.AbsenceRequest.start_date >= start_period,
            models.AbsenceRequest.end_date <= end_period
        )
    ).all()
    
    total_days = 0
    for request in approved_requests:
        days = calculate_business_days(request.start_date, request.end_date)
        total_days += days
    
    return total_days

def calculate_sick_days(db: Session, user_id: int, year: int = None) -> int:
    """Calculer le nombre total de jours de maladie pour un utilisateur"""
    if year is None:
        year = datetime.now().year
    
    # Période de l'année civile
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    total_sick_days = 0
    
    # Jours de maladie via AbsenceRequest
    sick_requests = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == user_id,
            models.AbsenceRequest.type == models.AbsenceType.MALADIE,
            models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE,
            models.AbsenceRequest.start_date >= start_date,
            models.AbsenceRequest.end_date <= end_date
        )
    ).all()
    
    for request in sick_requests:
        days = calculate_business_days(request.start_date, request.end_date)
        total_sick_days += days
    
    # Jours de maladie via SicknessDeclaration
    from .sickness import get_sickness_declarations
    sick_declarations = db.query(models.SicknessDeclaration).filter(
        and_(
            models.SicknessDeclaration.user_id == user_id,
            models.SicknessDeclaration.start_date >= start_date,
            models.SicknessDeclaration.end_date <= end_date
        )
    ).all()
    
    for declaration in sick_declarations:
        days = calculate_business_days(declaration.start_date, declaration.end_date)
        total_sick_days += days
    
    return total_sick_days

def get_dashboard_data(db: Session, user_id: int) -> schemas.DashboardData:
    """Récupérer les données du tableau de bord pour un utilisateur"""
    user = get_user(db, user_id)
    if not user:
        raise ValueError("Utilisateur non trouvé")
    
    # Utiliser l'année courante pour le calcul
    current_year = datetime.now().year
    used_days = calculate_used_leave_days(db, user_id, current_year)
    total_days = user.annual_leave_days
    remaining_days = total_days - used_days
    sick_days = calculate_sick_days(db, user_id, current_year)
    
    # Compter les demandes en attente et approuvées
    pending_count = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == user_id,
            models.AbsenceRequest.status == models.AbsenceStatus.EN_ATTENTE
        )
    ).count()
    
    approved_count = db.query(models.AbsenceRequest).filter(
        and_(
            models.AbsenceRequest.user_id == user_id,
            models.AbsenceRequest.status == models.AbsenceStatus.APPROUVE
        )
    ).count()
    
    return schemas.DashboardData(
        remaining_leave_days=max(0, remaining_days),
        used_leave_days=used_days,
        total_leave_days=total_days,
        pending_requests=pending_count,
        approved_requests=approved_count,
        sick_days=sick_days
    )

def get_user_absence_summary(db: Session, user_id: int) -> schemas.UserAbsenceSummary:
    """Récupérer le résumé des absences d'un utilisateur"""
    user = get_user(db, user_id)
    if not user:
        raise ValueError("Utilisateur non trouvé")
    
    # Récupérer toutes les absences de l'utilisateur
    from .absences import get_absence_requests
    from .sickness import get_sickness_declarations
    all_requests = get_absence_requests(db, user_id=user_id, limit=1000)
    all_sickness_declarations = get_sickness_declarations(db, user_id=user_id, limit=1000)
    
    # Calculer les statistiques
    total_absence_days = 0
    vacation_days = 0
    sick_days = 0
    pending_requests = 0
    approved_requests = 0
    
    # Traiter les demandes d'absence
    for request in all_requests:
        if request.status == models.AbsenceStatus.APPROUVE:
            days = calculate_business_days(request.start_date, request.end_date)
            total_absence_days += days
            
            if request.type == models.AbsenceType.VACANCES:
                vacation_days += days
            elif request.type == models.AbsenceType.MALADIE:
                sick_days += days
            
            approved_requests += 1
        elif request.status == models.AbsenceStatus.EN_ATTENTE:
            pending_requests += 1
    
    # Traiter les déclarations de maladie
    for declaration in all_sickness_declarations:
        days = calculate_business_days(declaration.start_date, declaration.end_date)
        sick_days += days
        total_absence_days += days
    
    # Récupérer les 10 absences les plus récentes
    recent_requests = db.query(models.AbsenceRequest).filter(
        models.AbsenceRequest.user_id == user_id
    ).order_by(models.AbsenceRequest.created_at.desc()).limit(10).all()
    
    return schemas.UserAbsenceSummary(
        user=user,
        total_absence_days=total_absence_days,
        vacation_days=vacation_days,
        sick_days=sick_days,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        recent_absences=recent_requests
    ) 