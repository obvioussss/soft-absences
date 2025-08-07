import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
import aiofiles
from pathlib import Path

class FileService:
    def __init__(self):
        self.upload_dir = Path("uploads/sickness_declarations")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_extensions = {".pdf"}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def _is_allowed_file(self, filename: str) -> bool:
        """Vérifier si l'extension du fichier est autorisée"""
        return Path(filename).suffix.lower() in self.allowed_extensions
    
    async def save_pdf(self, file: UploadFile) -> tuple[str, str]:
        """
        Sauvegarder un fichier PDF uploadé
        Returns: (filename, file_path)
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier manquant")
        
        if not self._is_allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont autorisés")
        
        # Vérifier la taille du fichier
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (max 10MB)")
        
        # Générer un nom de fichier unique
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = self.upload_dir / unique_filename
        
        # Sauvegarder le fichier
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde: {str(e)}")
        
        return file.filename, str(file_path)
    
    def get_file_path(self, filename: str) -> Optional[str]:
        """Obtenir le chemin complet d'un fichier"""
        file_path = self.upload_dir / filename
        if file_path.exists():
            return str(file_path)
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """Supprimer un fichier"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {file_path}: {e}")
        return False

# Instance globale
file_service = FileService()