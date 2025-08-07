from sqlalchemy.orm import Session
from typing import Optional, List

from app import models, schemas

def get_sickness_declaration(db: Session, declaration_id: int) -> Optional[models.SicknessDeclaration]:
    """Récupérer une déclaration de maladie par ID"""
    return db.query(models.SicknessDeclaration).filter(models.SicknessDeclaration.id == declaration_id).first()

def get_sickness_declarations(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[models.SicknessDeclaration]:
    """Récupérer les déclarations de maladie avec filtres optionnels"""
    query = db.query(models.SicknessDeclaration)
    
    if user_id:
        query = query.filter(models.SicknessDeclaration.user_id == user_id)
    
    return query.order_by(models.SicknessDeclaration.created_at.desc()).offset(skip).limit(limit).all()

def create_sickness_declaration(db: Session, declaration: schemas.SicknessDeclarationCreate, user_id: int) -> models.SicknessDeclaration:
    """Créer une nouvelle déclaration de maladie"""
    db_declaration = models.SicknessDeclaration(
        user_id=user_id,
        start_date=declaration.start_date,
        end_date=declaration.end_date,
        description=declaration.description
    )
    db.add(db_declaration)
    db.commit()
    db.refresh(db_declaration)
    return db_declaration

def update_sickness_declaration_file(db: Session, declaration_id: int, filename: str, file_path: str) -> Optional[models.SicknessDeclaration]:
    """Mettre à jour les informations de fichier d'une déclaration de maladie"""
    db_declaration = get_sickness_declaration(db, declaration_id)
    if not db_declaration:
        return None
    
    db_declaration.pdf_filename = filename
    db_declaration.pdf_path = file_path
    db.commit()
    db.refresh(db_declaration)
    return db_declaration

def mark_sickness_declaration_email_sent(db: Session, declaration_id: int) -> Optional[models.SicknessDeclaration]:
    """Marquer une déclaration comme ayant été envoyée par email"""
    db_declaration = get_sickness_declaration(db, declaration_id)
    if not db_declaration:
        return None
    
    db_declaration.email_sent = True
    db.commit()
    db.refresh(db_declaration)
    return db_declaration

def mark_sickness_declaration_viewed(db: Session, declaration_id: int) -> Optional[models.SicknessDeclaration]:
    """Marquer une déclaration comme vue par l'admin"""
    db_declaration = get_sickness_declaration(db, declaration_id)
    if not db_declaration:
        return None
    
    db_declaration.viewed_by_admin = True
    db.commit()
    db.refresh(db_declaration)
    return db_declaration 