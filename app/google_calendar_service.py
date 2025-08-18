"""
Service de synchronisation avec Google Calendar
"""
import os
import json
import base64
from datetime import datetime, date
from typing import Optional, Dict, Any
import logging

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app import models

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service pour synchroniser les absences avec Google Calendar"""
    
    def __init__(self):
        self.service = None
        self.calendar_id = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialise le service Google Calendar"""
        try:
            # Récupérer les credentials depuis les variables d'environnement
            credentials_json = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
            self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
            
            if not credentials_json or not self.calendar_id:
                logger.warning("Configuration Google Calendar manquante. Synchronisation désactivée.")
                return
            
            # Décoder les credentials (encodés en base64)
            try:
                credentials_data = json.loads(base64.b64decode(credentials_json).decode('utf-8'))
            except Exception as e:
                logger.error(f"Erreur lors du décodage des credentials Google Calendar: {e}")
                return
            
            # Créer les credentials
            credentials = Credentials.from_service_account_info(
                credentials_data,
                scopes=['https://www.googleapis.com/auth/calendar']
            )
            
            # Construire le service
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Service Google Calendar initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service Google Calendar: {e}")
            self.service = None
    
    def is_configured(self) -> bool:
        """Vérifie si le service est configuré"""
        return self.service is not None and self.calendar_id is not None
    
    def create_event(self, absence_request: models.AbsenceRequest) -> Optional[str]:
        """
        Crée un événement dans Google Calendar pour une demande d'absence
        Retourne l'ID de l'événement créé ou None en cas d'erreur
        """
        if not self.is_configured():
            logger.warning("Service Google Calendar non configuré")
            return None
        
        try:
            # Créer l'événement
            event_data = self._build_event_data(absence_request)
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_data
            ).execute()
            
            event_id = event.get('id')
            logger.info(f"Événement Google Calendar créé: {event_id}")
            return event_id
            
        except HttpError as e:
            logger.error(f"Erreur HTTP lors de la création de l'événement Google Calendar: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'événement Google Calendar: {e}")
            return None
    
    def update_event(self, event_id: str, absence_request: models.AbsenceRequest) -> bool:
        """
        Met à jour un événement existant dans Google Calendar
        Retourne True si la mise à jour a réussi, False sinon
        """
        if not self.is_configured():
            logger.warning("Service Google Calendar non configuré")
            return False
        
        try:
            # Construire les données de l'événement
            event_data = self._build_event_data(absence_request)
            
            # Mettre à jour l'événement
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            
            logger.info(f"Événement Google Calendar mis à jour: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Erreur HTTP lors de la mise à jour de l'événement Google Calendar: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'événement Google Calendar: {e}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Supprime un événement de Google Calendar
        Retourne True si la suppression a réussi, False sinon
        """
        if not self.is_configured():
            logger.warning("Service Google Calendar non configuré")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Événement Google Calendar supprimé: {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.info(f"Événement Google Calendar déjà supprimé: {event_id}")
                return True
            logger.error(f"Erreur HTTP lors de la suppression de l'événement Google Calendar: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'événement Google Calendar: {e}")
            return False
    
    def _build_event_data(self, absence_request: models.AbsenceRequest) -> Dict[str, Any]:
        """Construit les données d'un événement Google Calendar"""
        
        # Déterminer le titre et la couleur selon le type et le statut
        type_label = "Vacances" if absence_request.type == models.AbsenceType.VACANCES else "Maladie"
        status_emoji = {
            models.AbsenceStatus.EN_ATTENTE: "⏳",
            models.AbsenceStatus.APPROUVE: "✅", 
            models.AbsenceStatus.REFUSE: "❌"
        }
        
        emoji = status_emoji.get(absence_request.status, "")
        title = f"{emoji} {absence_request.user.first_name} {absence_request.user.last_name} - {type_label}"
        
        # Déterminer la couleur selon le statut
        color_id = {
            models.AbsenceStatus.EN_ATTENTE: "5",  # Jaune
            models.AbsenceStatus.APPROUVE: "10",   # Vert
            models.AbsenceStatus.REFUSE: "4"       # Rouge
        }.get(absence_request.status, "1")  # Bleu par défaut
        
        # Description détaillée
        description_parts = [
            f"Employé: {absence_request.user.first_name} {absence_request.user.last_name}",
            f"Email: {absence_request.user.email}",
            f"Type: {type_label}",
            f"Statut: {absence_request.status.value.replace('_', ' ').title()}",
        ]
        
        if absence_request.reason:
            description_parts.append(f"Motif: {absence_request.reason}")
        
        if absence_request.admin_comment:
            description_parts.append(f"Commentaire admin: {absence_request.admin_comment}")
        
        description = "\n".join(description_parts)
        
        # Convertir les dates en format ISO pour Google Calendar
        # Les événements "all-day" utilisent le format date uniquement
        start_date = absence_request.start_date.isoformat()
        # Pour les événements all-day, la date de fin doit être le jour suivant
        end_date = absence_request.end_date
        from datetime import timedelta
        end_date_plus_one = end_date + timedelta(days=1)
        end_date_iso = end_date_plus_one.isoformat()
        
        event_data = {
            'summary': title,
            'description': description,
            'start': {
                'date': start_date,  # Événement sur toute la journée
                'timeZone': 'Europe/Paris'
            },
            'end': {
                'date': end_date_iso,  # Jour suivant pour les événements all-day
                'timeZone': 'Europe/Paris'
            },
            'colorId': color_id,
            'transparency': 'transparent' if absence_request.status == models.AbsenceStatus.REFUSE else 'opaque'
        }
        
        return event_data

    def create_sickness_event(self, sickness_declaration: models.SicknessDeclaration) -> Optional[str]:
        """
        Crée un événement dans Google Calendar pour une déclaration de maladie
        Retourne l'ID de l'événement créé ou None en cas d'erreur
        """
        if not self.is_configured():
            logger.warning("Service Google Calendar non configuré")
            return None
        
        try:
            # Créer l'événement pour la déclaration de maladie
            event_data = self._build_sickness_event_data(sickness_declaration)
            
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event_data
            ).execute()
            
            event_id = event.get('id')
            logger.info(f"Événement Google Calendar créé pour déclaration maladie: {event_id}")
            return event_id
            
        except HttpError as e:
            logger.error(f"Erreur HTTP lors de la création de l'événement maladie Google Calendar: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'événement maladie Google Calendar: {e}")
            return None

    def _build_sickness_event_data(self, sickness_declaration: models.SicknessDeclaration) -> Dict[str, Any]:
        """Construit les données d'un événement Google Calendar pour une déclaration de maladie"""
        
        email_status = " ✉️" if sickness_declaration.email_sent else " ❌"
        title = f"🏥 {sickness_declaration.user.first_name} {sickness_declaration.user.last_name} - Arrêt maladie{email_status}"
        
        # Description détaillée
        description_parts = [
            f"Employé: {sickness_declaration.user.first_name} {sickness_declaration.user.last_name}",
            f"Email: {sickness_declaration.user.email}",
            f"Type: Arrêt maladie",
            f"Email envoyé: {'Oui' if sickness_declaration.email_sent else 'Non'}",
            f"Vu par admin: {'Oui' if sickness_declaration.viewed_by_admin else 'Non'}",
        ]
        
        if sickness_declaration.description:
            description_parts.append(f"Description: {sickness_declaration.description}")
        
        if sickness_declaration.pdf_filename:
            description_parts.append(f"Document: {sickness_declaration.pdf_filename}")
        
        description = "\n".join(description_parts)
        
        # Convertir les dates
        start_date = sickness_declaration.start_date.isoformat()
        from datetime import timedelta
        end_date_plus_one = sickness_declaration.end_date + timedelta(days=1)
        end_date_iso = end_date_plus_one.isoformat()
        
        event_data = {
            'summary': title,
            'description': description,
            'start': {
                'date': start_date,
                'timeZone': 'Europe/Paris'
            },
            'end': {
                'date': end_date_iso,
                'timeZone': 'Europe/Paris'
            },
            'colorId': '11',  # Rouge pour les arrêts maladie
            'transparency': 'opaque'
        }
        
        return event_data


# Instance globale du service
google_calendar_service = GoogleCalendarService()