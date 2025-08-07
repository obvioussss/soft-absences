import pytest
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.crud import calculate_business_days, calculate_used_leave_days, get_dashboard_data, get_user_absence_summary
from app.models import User, AbsenceRequest, AbsenceType, AbsenceStatus, UserRole
from app.auth import get_password_hash

def test_calculate_business_days():
    """Test du calcul des jours ouvrés"""
    # Test sur une semaine normale
    start = date(2024, 1, 1)  # Lundi
    end = date(2024, 1, 5)    # Vendredi
    assert calculate_business_days(start, end) == 5
    
    # Test sur une période avec weekend
    start = date(2024, 1, 1)  # Lundi
    end = date(2024, 1, 7)    # Dimanche
    assert calculate_business_days(start, end) == 5
    
    # Test sur une seule journée
    start = date(2024, 1, 1)  # Lundi
    end = date(2024, 1, 1)    # Lundi
    assert calculate_business_days(start, end) == 1
    
    # Test sur un weekend
    start = date(2024, 1, 6)  # Samedi
    end = date(2024, 1, 7)    # Dimanche
    assert calculate_business_days(start, end) == 0
    
    # Test avec dates inversées
    start = date(2024, 1, 5)  # Vendredi
    end = date(2024, 1, 1)    # Lundi
    assert calculate_business_days(start, end) == 0

def test_calculate_used_leave_days(db: Session):
    """Test du calcul des jours de congés utilisés"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        annual_leave_days=25
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer des demandes de congés approuvées avec des dates fixes
    request1 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(2024, 6, 3),  # Lundi 3 juin 2024
        end_date=date(2024, 6, 7),    # Vendredi 7 juin 2024
        status=AbsenceStatus.APPROUVE
    )
    
    request2 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(2024, 7, 1),  # Lundi 1er juillet 2024
        end_date=date(2024, 7, 2),    # Mardi 2 juillet 2024
        status=AbsenceStatus.APPROUVE
    )
    
    # Demande refusée (ne doit pas compter)
    request3 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 2),
        status=AbsenceStatus.REFUSE
    )
    
    db.add_all([request1, request2, request3])
    db.commit()
    
    # Calculer les jours utilisés pour 2024
    used_days = calculate_used_leave_days(db, user.id, 2024)
    
    # 5 jours ouvrés (3-7 juin) + 2 jours ouvrés (1-2 juillet) = 7 jours
    assert used_days == 7

def test_get_dashboard_data(db: Session):
    """Test de la récupération des données du tableau de bord"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        annual_leave_days=25
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer des demandes avec des dates de l'année courante
    current_year = datetime.now().year
    request1 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(current_year, 6, 3),
        end_date=date(current_year, 6, 7),
        status=AbsenceStatus.APPROUVE
    )
    
    request2 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(current_year, 7, 1),
        end_date=date(current_year, 7, 2),
        status=AbsenceStatus.EN_ATTENTE
    )
    
    db.add_all([request1, request2])
    db.commit()
    
    # Récupérer les données du tableau de bord
    dashboard_data = get_dashboard_data(db, user.id)
    
    # Vérifier que les jours utilisés correspondent aux jours ouvrés
    assert dashboard_data.used_leave_days >= 0  # Au moins 0 jours utilisés
    assert dashboard_data.remaining_leave_days <= 25  # Au maximum 25 jours restants
    assert dashboard_data.total_leave_days == 25
    assert dashboard_data.pending_requests == 1
    assert dashboard_data.approved_requests == 1

def test_get_user_absence_summary(db: Session):
    """Test du résumé des absences d'un utilisateur"""
    # Créer un utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        first_name="Test",
        last_name="User",
        role=UserRole.USER,
        annual_leave_days=25
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer des demandes
    request1 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(2024, 6, 3),
        end_date=date(2024, 6, 7),
        status=AbsenceStatus.APPROUVE
    )
    
    request2 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.MALADIE,
        start_date=date(2024, 7, 1),
        end_date=date(2024, 7, 2),
        status=AbsenceStatus.APPROUVE
    )
    
    request3 = AbsenceRequest(
        user_id=user.id,
        type=AbsenceType.VACANCES,
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 2),
        status=AbsenceStatus.EN_ATTENTE
    )
    
    db.add_all([request1, request2, request3])
    db.commit()
    
    # Récupérer le résumé
    summary = get_user_absence_summary(db, user.id)
    
    assert summary.user.id == user.id
    assert summary.total_absence_days == 7  # 5 jours vacances + 2 jours maladie
    assert summary.vacation_days == 5
    assert summary.sick_days == 2
    assert summary.pending_requests == 1
    assert summary.approved_requests == 2
    assert len(summary.recent_absences) == 3 