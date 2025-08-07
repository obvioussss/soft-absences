import os
import json
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app import models

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    def __init__(self):
        self.calendar_id = "hello.obvious@gmail.com"
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialise le service Google Calendar avec les credentials."""
        try:
            # Récupérer les credentials depuis les variables d'environnement
            credentials_json = os.getenv('GOOGLE_CALENDAR_CREDENTIALS')
            if not credentials_json:
                logger.warning("GOOGLE_CALENDAR_CREDENTIALS non configuré. Synchronisation Google Calendar désactivée.")
                return
            
            # Parser les credentials JSON
            credentials_info = json.loads(credentials_json)
            
            # Créer les credentials avec les scopes nécessaires
            scopes = ['https://www.googleapis.com/auth/calendar']
            credentials = Credentials.from_service_account_info(
                credentials_info, scopes=scopes
            )
            
            # Construire le service
            self.service = build('calendar', 'v3', credentials=credentials)
            logger.info("Service Google Calendar initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du service Google Calendar: {e}")
            self.service = None
    
    def is_enabled(self) -> bool:
        """Vérifie si le service Google Calendar est activé."""
        return self.service is not None
    
    def create_absence_event(self, absence_request: models.AbsenceRequest) -> Optional[str]:
        """
        Crée un événement dans Google Calendar pour une demande d'absence approuvée.
        
        Args:
            absence_request: La demande d'absence approuvée
            
        Returns:
            L'ID de l'événement créé ou None en cas d'erreur
        """
        if not self.is_enabled():
            logger.warning("Service Google Calendar non disponible")
            return None
        
        try:
            # Construire le titre de l'événement
            user_name = f"{absence_request.user.first_name} {absence_request.user.last_name}"
            absence_type = "Vacances" if absence_request.type == models.AbsenceType.VACANCES else "Maladie"
            event_title = f"{absence_type} - {user_name}"
            
            # Construire la description
            description = f"Demande d'absence approuvée\n"
            description += f"Employé: {user_name}\n"
            description += f"Type: {absence_type}\n"
            description += f"Du: {absence_request.start_date.strftime('%d/%m/%Y')}\n"
            description += f"Au: {absence_request.end_date.strftime('%d/%m/%Y')}\n"
            if absence_request.reason:
                description += f"Motif: {absence_request.reason}\n"
            if absence_request.admin_comment:
                description += f"Commentaire admin: {absence_request.admin_comment}"
            
            # Créer l'événement (événement de toute la journée)
            event = {
                'summary': event_title,
                'description': description,
                'start': {
                    'date': absence_request.start_date.isoformat(),
                    'timeZone': 'Europe/Paris',
                },
                'end': {
                    # Pour un événement de toute la journée, la date de fin doit être le jour suivant
                    'date': (absence_request.end_date + timedelta(days=1)).isoformat(),
                    'timeZone': 'Europe/Paris',
                },
                'colorId': '9' if absence_request.type == models.AbsenceType.VACANCES else '11',  # Bleu pour vacances, rouge pour maladie
            }
            
            # Insérer l'événement dans le calendrier
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            logger.info(f"Événement Google Calendar créé avec succès: {event_id}")
            return event_id
            
        except HttpError as e:
            logger.error(f"Erreur HTTP lors de la création de l'événement Google Calendar: {e}")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'événement Google Calendar: {e}")
            return None
    
    def update_absence_event(self, event_id: str, absence_request: models.AbsenceRequest) -> bool:
        """
        Met à jour un événement existant dans Google Calendar.
        
        Args:
            event_id: L'ID de l'événement à mettre à jour
            absence_request: La demande d'absence mise à jour
            
        Returns:
            True si la mise à jour a réussi, False sinon
        """
        if not self.is_enabled():
            logger.warning("Service Google Calendar non disponible")
            return False
        
        try:
            # Récupérer l'événement existant
            existing_event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Construire le nouveau titre et description
            user_name = f"{absence_request.user.first_name} {absence_request.user.last_name}"
            absence_type = "Vacances" if absence_request.type == models.AbsenceType.VACANCES else "Maladie"
            event_title = f"{absence_type} - {user_name}"
            
            description = f"Demande d'absence approuvée\n"
            description += f"Employé: {user_name}\n"
            description += f"Type: {absence_type}\n"
            description += f"Du: {absence_request.start_date.strftime('%d/%m/%Y')}\n"
            description += f"Au: {absence_request.end_date.strftime('%d/%m/%Y')}\n"
            if absence_request.reason:
                description += f"Motif: {absence_request.reason}\n"
            if absence_request.admin_comment:
                description += f"Commentaire admin: {absence_request.admin_comment}"
            
            # Mettre à jour l'événement
            existing_event['summary'] = event_title
            existing_event['description'] = description
            existing_event['start'] = {
                'date': absence_request.start_date.isoformat(),
                'timeZone': 'Europe/Paris',
            }
            existing_event['end'] = {
                'date': (absence_request.end_date + timedelta(days=1)).isoformat(),
                'timeZone': 'Europe/Paris',
            }
            existing_event['colorId'] = '9' if absence_request.type == models.AbsenceType.VACANCES else '11'
            
            # Sauvegarder les modifications
            self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=existing_event
            ).execute()
            
            logger.info(f"Événement Google Calendar mis à jour avec succès: {event_id}")
            return True
            
        except HttpError as e:
            logger.error(f"Erreur HTTP lors de la mise à jour de l'événement Google Calendar: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'événement Google Calendar: {e}")
            return False
    
    def delete_absence_event(self, event_id: str) -> bool:
        """
        Supprime un événement dans Google Calendar.
        
        Args:
            event_id: L'ID de l'événement à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        if not self.is_enabled():
            logger.warning("Service Google Calendar non disponible")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Événement Google Calendar supprimé avec succès: {event_id}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Événement Google Calendar non trouvé: {event_id}")
                return True  # L'événement n'existe plus, c'est le résultat souhaité
            logger.error(f"Erreur HTTP lors de la suppression de l'événement Google Calendar: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'événement Google Calendar: {e}")
            return False
    
    def get_absence_events(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """
        Récupère les événements d'absence dans une période donnée.
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des événements trouvés
        """
        if not self.is_enabled():
            logger.warning("Service Google Calendar non disponible")
            return []
        
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Récupéré {len(events)} événements Google Calendar")
            return events
            
        except HttpError as e:
            logger.error(f"Erreur HTTP lors de la récupération des événements Google Calendar: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des événements Google Calendar: {e}")
            return []


# Instance globale du service
google_calendar_service = GoogleCalendarService()