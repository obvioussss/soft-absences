from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, Text, ForeignKey, Enum
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, timezone
import enum

class Base(DeclarativeBase):
    pass

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class AbsenceType(enum.Enum):
    VACANCES = "vacances"
    MALADIE = "maladie"

class AbsenceStatus(enum.Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    annual_leave_days = Column(Integer, default=25, nullable=False)  # Jours de congés annuels
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    absence_requests = relationship("AbsenceRequest", foreign_keys="AbsenceRequest.user_id", back_populates="user")
    approved_requests = relationship("AbsenceRequest", foreign_keys="AbsenceRequest.approved_by_id", back_populates="approved_by")
    sickness_declarations = relationship("SicknessDeclaration", back_populates="user")

class AbsenceRequest(Base):
    __tablename__ = "absence_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(AbsenceType), nullable=False)
    start_date = Column(Date, nullable=False)  # Utilise Date au lieu de DateTime
    end_date = Column(Date, nullable=False)    # Utilise Date au lieu de DateTime
    reason = Column(Text, nullable=True)
    status = Column(Enum(AbsenceStatus), default=AbsenceStatus.EN_ATTENTE, nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    admin_comment = Column(Text, nullable=True)
    google_calendar_event_id = Column(String, nullable=True)  # ID de l'événement Google Calendar
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    user = relationship("User", foreign_keys=[user_id], back_populates="absence_requests")
    approved_by = relationship("User", foreign_keys=[approved_by_id], back_populates="approved_requests")

class SicknessDeclaration(Base):
    __tablename__ = "sickness_declarations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    pdf_filename = Column(String, nullable=True)  # Nom du fichier PDF uploadé
    pdf_path = Column(String, nullable=True)      # Chemin vers le fichier sur le serveur
    email_sent = Column(Boolean, default=False, nullable=False)  # Si l'email a été envoyé
    viewed_by_admin = Column(Boolean, default=False, nullable=False)  # Si vu par l'admin
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relations
    user = relationship("User", back_populates="sickness_declarations")