from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app import models, schemas, crud, auth
from app.email_service import email_service
from app.file_service import file_service

router = APIRouter()

@router.get("/", response_model=list[schemas.SicknessDeclaration])
async def read_sickness_declarations(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupérer les déclarations de maladie (utilisateur: ses propres déclarations, admin: toutes)"""
    if current_user.role == models.UserRole.ADMIN:
        declarations = crud.get_sickness_declarations(db, skip=skip, limit=limit)
    else:
        declarations = crud.get_sickness_declarations(db, skip=skip, limit=limit, user_id=current_user.id)
    return declarations

@router.post("/", response_model=schemas.SicknessDeclaration)
async def create_sickness_declaration(
    start_date: str = Form(...),
    end_date: str = Form(...),
    description: Optional[str] = Form(None),
    pdf_file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Créer une nouvelle déclaration de maladie avec PDF"""
    # Seuls les utilisateurs normaux peuvent créer des déclarations
    if current_user.role == models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Les administrateurs ne peuvent pas créer de déclarations de maladie")
    
    # Valider les données
    from datetime import date
    try:
        start_date_obj = date.fromisoformat(start_date)
        end_date_obj = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide (YYYY-MM-DD)")
    
    if start_date_obj > end_date_obj:
        raise HTTPException(status_code=400, detail="La date de fin doit être postérieure à la date de début")
    
    # Créer la déclaration
    declaration_data = schemas.SicknessDeclarationCreate(
        start_date=start_date_obj,
        end_date=end_date_obj,
        description=description
    )
    
    db_declaration = crud.create_sickness_declaration(db=db, declaration=declaration_data, user_id=current_user.id)
    
    # Sauvegarder le fichier PDF
    try:
        original_filename, file_path = await file_service.save_pdf(pdf_file)
        crud.update_sickness_declaration_file(db, db_declaration.id, original_filename, file_path)
        
        # Envoyer l'email avec le PDF
        user_name = f"{current_user.first_name} {current_user.last_name}"
        # Envoyer l'email à l'admin et à l'utilisateur
        admin_users = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).all()
        admin_emails = [admin.email for admin in admin_users] or ["hello.obvious@gmail.com"]
        recipients = list({*(admin_emails), current_user.email})
        email_sent = email_service.send_sickness_declaration_email(
            user_name=user_name,
            to_emails=recipients,
            start_date=str(start_date_obj),
            end_date=str(end_date_obj),
            description=description,
            pdf_path=file_path
        )
        
        if email_sent:
            crud.mark_sickness_declaration_email_sent(db, db_declaration.id)
        
        # Rafraîchir pour obtenir les données mises à jour
        db.refresh(db_declaration)
        
    except Exception as e:
        # Si l'upload échoue, supprimer la déclaration créée
        db.delete(db_declaration)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'upload du fichier: {str(e)}")
    
    return db_declaration

@router.get("/{declaration_id}/pdf")
async def download_sickness_pdf(
    declaration_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Servir le PDF d'une déclaration en affichage inline"""
    declaration = crud.get_sickness_declaration(db, declaration_id)
    if not declaration:
        raise HTTPException(status_code=404, detail="Déclaration non trouvée")
    if current_user.role != models.UserRole.ADMIN and declaration.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    if not declaration.pdf_path:
        raise HTTPException(status_code=404, detail="Aucun document PDF pour cette déclaration")
    
    import os
    if not os.path.exists(declaration.pdf_path):
        raise HTTPException(status_code=404, detail="Fichier PDF non trouvé sur le serveur")
    
    with open(declaration.pdf_path, 'rb') as f:
        data = f.read()
    headers = {
        "Content-Type": "application/pdf",
        "Content-Disposition": f"inline; filename=\"{declaration.pdf_filename or 'document.pdf'}\""
    }
    return Response(content=data, headers=headers)

@router.get("/{declaration_id}", response_model=schemas.SicknessDeclaration)
async def read_sickness_declaration(
    declaration_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupérer une déclaration de maladie spécifique"""
    db_declaration = crud.get_sickness_declaration(db, declaration_id=declaration_id)
    if db_declaration is None:
        raise HTTPException(status_code=404, detail="Déclaration non trouvée")
    
    # Vérifier que l'utilisateur peut accéder à cette déclaration
    if current_user.role != models.UserRole.ADMIN and db_declaration.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Si c'est un admin qui consulte, marquer comme vue et envoyer un email
    if current_user.role == models.UserRole.ADMIN and not db_declaration.viewed_by_admin:
        crud.mark_sickness_declaration_viewed(db, declaration_id)
        
        # Envoyer un email à l'utilisateur pour l'informer
        user_name = f"{db_declaration.user.first_name} {db_declaration.user.last_name}"
        admin_name = f"{current_user.first_name} {current_user.last_name}"
        
        email_service.send_sickness_declaration_viewed_notification(
            user_email=db_declaration.user.email,
            user_name=user_name,
            start_date=str(db_declaration.start_date),
            end_date=str(db_declaration.end_date),
            admin_name=admin_name
        )
        
        db.refresh(db_declaration)
    
    return db_declaration

@router.get("/admin/unviewed-count")
async def get_unviewed_declarations_count(
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Obtenir le nombre de déclarations non vues par l'admin"""
    count = db.query(models.SicknessDeclaration).filter(
        models.SicknessDeclaration.viewed_by_admin == False
    ).count()
    return {"unviewed_count": count}

@router.post("/{declaration_id}/mark-viewed")
async def mark_declaration_as_viewed(
    declaration_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Marquer une déclaration comme vue par l'admin"""
    declaration = crud.get_sickness_declaration(db, declaration_id)
    if not declaration:
        raise HTTPException(status_code=404, detail="Déclaration non trouvée")
    
    # Marquer comme vue
    crud.mark_sickness_declaration_viewed(db, declaration_id)
    
    # Envoyer un email à l'utilisateur pour l'informer
    user_name = f"{declaration.user.first_name} {declaration.user.last_name}"
    admin_name = f"{current_user.first_name} {current_user.last_name}"
    
    email_service.send_sickness_declaration_viewed_notification(
        user_email=declaration.user.email,
        user_name=user_name,
        start_date=str(declaration.start_date),
        end_date=str(declaration.end_date),
        admin_name=admin_name
    )
    
    return {"message": "Déclaration marquée comme vue et email envoyé"}

@router.post("/{declaration_id}/resend-email")
async def resend_declaration_email(
    declaration_id: int,
    current_user: models.User = Depends(auth.get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Renvoyer l'email d'une déclaration de maladie"""
    declaration = crud.get_sickness_declaration(db, declaration_id)
    if not declaration:
        raise HTTPException(status_code=404, detail="Déclaration non trouvée")
    
    if not declaration.pdf_filename or not declaration.pdf_path:
        raise HTTPException(status_code=400, detail="Aucun document PDF associé à cette déclaration")
    
    # Vérifier que le fichier existe
    import os
    if not os.path.exists(declaration.pdf_path):
        raise HTTPException(status_code=404, detail="Fichier PDF non trouvé sur le serveur")
    
    try:
        # Renvoyer l'email
        from app.email_service import EmailService
        email_service = EmailService()
        email_sent = email_service.send_sickness_declaration_email(
            user_name=f"{declaration.user.first_name} {declaration.user.last_name}",
            start_date=declaration.start_date,
            end_date=declaration.end_date,
            description=declaration.description,
            pdf_path=declaration.pdf_path,
            pdf_filename=declaration.pdf_filename
        )
        
        if email_sent:
            # Marquer l'email comme envoyé
            crud.mark_sickness_declaration_email_sent(db, declaration_id)
            return {"message": "Email renvoyé avec succès"}
        else:
            raise HTTPException(status_code=500, detail="Erreur lors de l'envoi de l'email")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi: {str(e)}")