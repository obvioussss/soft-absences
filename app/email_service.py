import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from dotenv import load_dotenv
from jinja2 import Template

load_dotenv()

class EmailService:
    def __init__(self):
        self._init_smtp_config()
        self._init_resend_config()
        self.use_resend = bool(self.resend_api_key)
        
    def _init_smtp_config(self):
        """Initialise la configuration SMTP"""
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_from = os.getenv("EMAIL_FROM")
        
    def _init_resend_config(self):
        """Initialise la configuration Resend"""
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.resend_from_email = os.getenv("RESEND_FROM_EMAIL", "noreply@votre-domaine.com")
        
    def _format_subject(self, subject: str) -> str:
        """Formater le sujet avec le préfixe standard"""
        prefix = "Gestion des absences - "
        if not subject.startswith(prefix):
            return f"{prefix}{subject}"
        return subject
    
    def send_email(self, to_emails: List[str], subject: str, body: str, html_body: str = None):
        """Envoyer un email via Resend ou SMTP"""
        formatted_subject = self._format_subject(subject)
        if self.use_resend:
            return self._send_email_resend(to_emails, formatted_subject, body, html_body)
        else:
            return self._send_email_smtp(to_emails, formatted_subject, body, html_body)
    
    def _send_email_resend(self, to_emails: List[str], subject: str, body: str, html_body: str = None):
        """Envoyer un email via Resend API"""
        if not self.resend_api_key:
            print("Configuration Resend manquante, email non envoyé")
            return False
            
        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": self.resend_from_email,
                "to": to_emails,
                "subject": subject,
                "text": body,
                "html": html_body if html_body else None
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"Email envoyé via Resend à {to_emails}")
                return True
            else:
                print(f"Erreur Resend: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email via Resend: {e}")
            return False
    
    def _send_email_smtp(self, to_emails: List[str], subject: str, body: str, html_body: str = None):
        """Envoyer un email via SMTP"""
        if not self.smtp_username or not self.smtp_password:
            print("Configuration email manquante, email non envoyé")
            return False
            
        try:
            msg = self._create_smtp_message(to_emails, subject, body, html_body)
            self._send_smtp_message(msg)
            print(f"Email envoyé via SMTP à {to_emails}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email via SMTP: {e}")
            return False
    
    def _create_smtp_message(self, to_emails: List[str], subject: str, body: str, html_body: str = None):
        """Crée un message SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = ', '.join(to_emails)
        
        # Ajouter le contenu texte
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Ajouter le contenu HTML si fourni
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        return msg
    
    def _send_smtp_message(self, msg):
        """Envoie un message SMTP"""
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
    
    def send_absence_request_notification(self, admin_emails: List[str], user_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None):
        """Notifier les admins d'une nouvelle demande d'absence"""
        subject = f"Nouvelle demande d'absence - {user_name}"
        body, html_body = self._create_absence_request_content(user_name, absence_type, start_date, end_date, reason)
        return self.send_email(admin_emails, subject, body, html_body)
    
    def _create_absence_request_content(self, user_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None):
        """Crée le contenu pour une notification de demande d'absence"""
        body = f"""
Bonjour,

Une nouvelle demande d'absence a été soumise :

Employé : {user_name}
Type : {absence_type}
Début : {start_date}
Fin : {end_date}
Raison : {reason or 'Non spécifiée'}

Veuillez vous connecter à l'application pour traiter cette demande.

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Nouvelle demande d'absence</h2>
    <p>Bonjour,</p>
    <p>Une nouvelle demande d'absence a été soumise :</p>
    <ul>
        <li><strong>Employé :</strong> {user_name}</li>
        <li><strong>Type :</strong> {absence_type}</li>
        <li><strong>Début :</strong> {start_date}</li>
        <li><strong>Fin :</strong> {end_date}</li>
        <li><strong>Raison :</strong> {reason or 'Non spécifiée'}</li>
    </ul>
    <p>Veuillez vous connecter à l'application pour traiter cette demande.</p>
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body
    
    def send_absence_status_notification(self, user_email: str, user_name: str, absence_type: str, status: str, admin_comment: str = None):
        """Notifier l'utilisateur du changement de statut de sa demande"""
        status_text = "approuvée" if status == "approuve" else "refusée"
        subject = f"Demande d'absence {status_text}"
        body, html_body = self._create_absence_status_content(user_name, absence_type, status_text, admin_comment)
        return self.send_email([user_email], subject, body, html_body)
    
    def _create_absence_status_content(self, user_name: str, absence_type: str, status_text: str, admin_comment: str = None):
        """Crée le contenu pour une notification de statut d'absence"""
        body = f"""
Bonjour {user_name},

Votre demande d'absence ({absence_type}) a été {status_text}.

{f"Commentaire de l'administrateur : {admin_comment}" if admin_comment else ""}

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Statut de votre demande d'absence</h2>
    <p>Bonjour {user_name},</p>
    <p>Votre demande d'absence ({absence_type}) a été <strong>{status_text}</strong>.</p>
    {f"<p><strong>Commentaire de l'administrateur :</strong> {admin_comment}</p>" if admin_comment else ""}
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body
    
    def send_absence_modification_notification(self, admin_emails: List[str], user_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None, request_id: int = None):
        """Notifier les admins de la modification d'une demande d'absence"""
        subject = f"Demande d'absence modifiée - {user_name}"
        body, html_body = self._create_absence_modification_content(user_name, absence_type, start_date, end_date, reason, request_id)
        return self.send_email(admin_emails, subject, body, html_body)
    
    def _create_absence_modification_content(self, user_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None, request_id: int = None):
        """Crée le contenu pour une notification de modification d'absence"""
        body = f"""
Bonjour,

Une demande d'absence a été modifiée :

Employé : {user_name}
ID de la demande : {request_id}
Type : {absence_type}
Début : {start_date}
Fin : {end_date}
Raison : {reason or 'Non spécifiée'}

Veuillez vous connecter à l'application pour consulter les détails de cette modification.

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Demande d'absence modifiée</h2>
    <p>Bonjour,</p>
    <p>Une demande d'absence a été modifiée :</p>
    <ul>
        <li><strong>Employé :</strong> {user_name}</li>
        <li><strong>ID de la demande :</strong> {request_id}</li>
        <li><strong>Type :</strong> {absence_type}</li>
        <li><strong>Début :</strong> {start_date}</li>
        <li><strong>Fin :</strong> {end_date}</li>
        <li><strong>Raison :</strong> {reason or 'Non spécifiée'}</li>
    </ul>
    <p>Veuillez vous connecter à l'application pour consulter les détails de cette modification.</p>
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body
    
    def send_absence_deletion_notification(self, admin_emails: List[str], user_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None, request_id: int = None):
        """Notifier les admins de la suppression d'une demande d'absence"""
        subject = f"Demande d'absence supprimée - {user_name}"
        body, html_body = self._create_absence_deletion_content(user_name, absence_type, start_date, end_date, reason, request_id)
        return self.send_email(admin_emails, subject, body, html_body)
    
    def _create_absence_deletion_content(self, user_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None, request_id: int = None):
        """Crée le contenu pour une notification de suppression d'absence"""
        body = f"""
Bonjour,

Une demande d'absence a été supprimée :

Employé : {user_name}
ID de la demande : {request_id}
Type : {absence_type}
Début : {start_date}
Fin : {end_date}
Raison : {reason or 'Non spécifiée'}

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Demande d'absence supprimée</h2>
    <p>Bonjour,</p>
    <p>Une demande d'absence a été supprimée :</p>
    <ul>
        <li><strong>Employé :</strong> {user_name}</li>
        <li><strong>ID de la demande :</strong> {request_id}</li>
        <li><strong>Type :</strong> {absence_type}</li>
        <li><strong>Début :</strong> {start_date}</li>
        <li><strong>Fin :</strong> {end_date}</li>
        <li><strong>Raison :</strong> {reason or 'Non spécifiée'}</li>
    </ul>
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body
    
    def send_admin_absence_notification(self, user_email: str, user_name: str, admin_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None, admin_comment: str = None):
        """Notifier l'utilisateur d'une absence créée par un admin"""
        subject = f"Absence créée par l'administrateur - {user_name}"
        body, html_body = self._create_admin_absence_content(user_name, admin_name, absence_type, start_date, end_date, reason, admin_comment)
        return self.send_email([user_email], subject, body, html_body)
    
    def _create_admin_absence_content(self, user_name: str, admin_name: str, absence_type: str, start_date: str, end_date: str, reason: str = None, admin_comment: str = None):
        """Crée le contenu pour une notification d'absence créée par un admin"""
        body = f"""
Bonjour {user_name},

Une absence a été créée pour vous par l'administrateur {admin_name} :

Type : {absence_type}
Début : {start_date}
Fin : {end_date}
Raison : {reason or 'Non spécifiée'}
{f"Commentaire de l'administrateur : {admin_comment}" if admin_comment else ""}

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Absence créée par l'administrateur</h2>
    <p>Bonjour {user_name},</p>
    <p>Une absence a été créée pour vous par l'administrateur <strong>{admin_name}</strong> :</p>
    <ul>
        <li><strong>Type :</strong> {absence_type}</li>
        <li><strong>Début :</strong> {start_date}</li>
        <li><strong>Fin :</strong> {end_date}</li>
        <li><strong>Raison :</strong> {reason or 'Non spécifiée'}</li>
    </ul>
    {f"<p><strong>Commentaire de l'administrateur :</strong> {admin_comment}</p>" if admin_comment else ""}
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body
    
    def send_sickness_declaration_email(self, user_name: str, user_email: str, start_date: str, end_date: str, description: str = None, pdf_path: str = None):
        """Envoyer un email de déclaration de maladie"""
        subject = f"Nouvelle déclaration de maladie - {user_name}"
        body, html_body = self._create_sickness_declaration_content(user_name, start_date, end_date, description)
        
        if pdf_path:
            return self.send_email_with_attachment([user_email], subject, body, html_body, pdf_path)
        else:
            return self.send_email([user_email], subject, body, html_body)
    
    def _create_sickness_declaration_content(self, user_name: str, start_date: str, end_date: str, description: str = None):
        """Crée le contenu pour une déclaration de maladie"""
        body = f"""
Bonjour,

Une nouvelle déclaration de maladie a été soumise :

Employé : {user_name}
Début : {start_date}
Fin : {end_date}
Description : {description or 'Non spécifiée'}

Veuillez vous connecter à l'application pour traiter cette déclaration.

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Nouvelle déclaration de maladie</h2>
    <p>Bonjour,</p>
    <p>Une nouvelle déclaration de maladie a été soumise :</p>
    <ul>
        <li><strong>Employé :</strong> {user_name}</li>
        <li><strong>Début :</strong> {start_date}</li>
        <li><strong>Fin :</strong> {end_date}</li>
        <li><strong>Description :</strong> {description or 'Non spécifiée'}</li>
    </ul>
    <p>Veuillez vous connecter à l'application pour traiter cette déclaration.</p>
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body
    
    def send_email_with_attachment(self, to_emails: list[str], subject: str, body: str, html_body: str = None, attachment_path: str = None):
        """Envoyer un email avec pièce jointe"""
        formatted_subject = self._format_subject(subject)
        if self.use_resend:
            return self._send_email_with_attachment_resend(to_emails, formatted_subject, body, html_body, attachment_path)
        else:
            return self._send_email_with_attachment_smtp(to_emails, formatted_subject, body, html_body, attachment_path)
    
    def _send_email_with_attachment_resend(self, to_emails: list[str], subject: str, body: str, html_body: str = None, attachment_path: str = None):
        """Envoyer un email avec pièce jointe via Resend"""
        if not self.resend_api_key:
            print("Configuration Resend manquante, email non envoyé")
            return False
            
        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": self.resend_from_email,
                "to": to_emails,
                "subject": subject,
                "text": body,
                "html": html_body if html_body else None
            }
            
            # Ajouter la pièce jointe si fournie
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    import base64
                    attachment_content = base64.b64encode(f.read()).decode('utf-8')
                    data["attachments"] = [{
                        "content": attachment_content,
                        "filename": os.path.basename(attachment_path)
                    }]
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"Email avec pièce jointe envoyé via Resend à {to_emails}")
                return True
            else:
                print(f"Erreur Resend: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email avec pièce jointe via Resend: {e}")
            return False
    
    def _send_email_with_attachment_smtp(self, to_emails: list[str], subject: str, body: str, html_body: str = None, attachment_path: str = None):
        """Envoyer un email avec pièce jointe via SMTP"""
        if not self.smtp_username or not self.smtp_password:
            print("Configuration email manquante, email non envoyé")
            return False
            
        try:
            msg = self._create_smtp_message_with_attachment(to_emails, subject, body, html_body, attachment_path)
            self._send_smtp_message(msg)
            print(f"Email avec pièce jointe envoyé via SMTP à {to_emails}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email avec pièce jointe via SMTP: {e}")
            return False
    
    def _create_smtp_message_with_attachment(self, to_emails: list[str], subject: str, body: str, html_body: str = None, attachment_path: str = None):
        """Crée un message SMTP avec pièce jointe"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.email_from
        msg['To'] = ', '.join(to_emails)
        
        # Ajouter le contenu texte
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Ajouter le contenu HTML si fourni
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Ajouter la pièce jointe si fournie
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                attachment = MIMEText(f.read(), 'base64', 'utf-8')
                attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(attachment)
        
        return msg
    
    def send_sickness_declaration_viewed_notification(self, user_email: str, user_name: str, start_date: str, end_date: str, admin_name: str):
        """Notifier l'utilisateur que sa déclaration de maladie a été vue"""
        subject = f"Déclaration de maladie consultée - {user_name}"
        body, html_body = self._create_sickness_viewed_content(user_name, start_date, end_date, admin_name)
        return self.send_email([user_email], subject, body, html_body)
    
    def _create_sickness_viewed_content(self, user_name: str, start_date: str, end_date: str, admin_name: str):
        """Crée le contenu pour une notification de consultation de déclaration de maladie"""
        body = f"""
Bonjour {user_name},

Votre déclaration de maladie du {start_date} au {end_date} a été consultée par l'administrateur {admin_name}.

Cordialement,
Système de gestion des absences
        """
        
        html_body = f"""
<html>
<body>
    <h2>Déclaration de maladie consultée</h2>
    <p>Bonjour {user_name},</p>
    <p>Votre déclaration de maladie du <strong>{start_date}</strong> au <strong>{end_date}</strong> a été consultée par l'administrateur <strong>{admin_name}</strong>.</p>
    <p>Cordialement,<br>Système de gestion des absences</p>
</body>
</html>
        """
        
        return body, html_body

# Instance globale
email_service = EmailService()