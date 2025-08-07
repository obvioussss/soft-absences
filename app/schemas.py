from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional
from app.models import UserRole, AbsenceType, AbsenceStatus

# Schémas pour les utilisateurs
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    annual_leave_days: int = 25

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    annual_leave_days: Optional[int] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# Schémas pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Schémas pour les demandes d'absence
class AbsenceRequestBase(BaseModel):
    type: AbsenceType
    start_date: date  # Utilise date au lieu de datetime
    end_date: date    # Utilise date au lieu de datetime
    reason: Optional[str] = None

class AbsenceRequestCreate(AbsenceRequestBase):
    pass

class AdminAbsenceCreate(AbsenceRequestBase):
    user_id: int  # L'admin spécifie pour quel utilisateur créer l'absence
    status: AbsenceStatus = AbsenceStatus.APPROUVE  # Par défaut approuvée puisque créée par l'admin
    admin_comment: Optional[str] = None

class AbsenceRequestUpdate(BaseModel):
    type: Optional[AbsenceType] = None
    start_date: Optional[date] = None  # Utilise date au lieu de datetime
    end_date: Optional[date] = None    # Utilise date au lieu de datetime
    reason: Optional[str] = None

class AbsenceRequestAdmin(BaseModel):
    status: AbsenceStatus
    admin_comment: Optional[str] = None

class AbsenceRequest(AbsenceRequestBase):
    id: int
    user_id: int
    status: AbsenceStatus
    approved_by_id: Optional[int] = None
    admin_comment: Optional[str] = None
    google_calendar_event_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Relations
    user: User
    approved_by: Optional[User] = None

    model_config = {"from_attributes": True}

# Schéma pour la réponse du calendrier
class CalendarEvent(BaseModel):
    id: int
    title: str
    start: date      # Utilise date au lieu de datetime
    end: date        # Utilise date au lieu de datetime
    type: AbsenceType
    status: AbsenceStatus
    user_name: str
    reason: Optional[str] = None
    event_source: str = "absence_request"  # "absence_request" ou "sickness_declaration"

# Schéma pour le tableau de bord avec compteur de congés
class DashboardData(BaseModel):
    remaining_leave_days: int
    used_leave_days: int
    total_leave_days: int
    pending_requests: int
    approved_requests: int

# Schéma pour le résumé des absences d'un utilisateur
class UserAbsenceSummary(BaseModel):
    user: User
    total_absence_days: int
    vacation_days: int
    sick_days: int
    pending_requests: int
    approved_requests: int
    recent_absences: list[AbsenceRequest]

# Schémas pour les déclarations de maladie
class SicknessDeclarationBase(BaseModel):
    start_date: date
    end_date: date
    description: Optional[str] = None

class SicknessDeclarationCreate(SicknessDeclarationBase):
    pass

class SicknessDeclaration(SicknessDeclarationBase):
    id: int
    user_id: int
    pdf_filename: Optional[str] = None
    pdf_path: Optional[str] = None
    email_sent: bool
    viewed_by_admin: bool
    created_at: datetime
    updated_at: datetime
    
    # Relations
    user: User

    model_config = {"from_attributes": True}