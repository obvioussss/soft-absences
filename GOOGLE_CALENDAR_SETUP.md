# Configuration Google Calendar

Ce document explique comment configurer l'intégration Google Calendar pour synchroniser automatiquement les demandes d'absence approuvées avec le calendrier `hello.obvious@gmail.com`.

## Prérequis

1. Un compte Google Cloud avec un projet actif
2. Accès au Google Calendar `hello.obvious@gmail.com`

## Étapes de configuration

### 1. Créer un Service Account

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Sélectionnez votre projet ou créez-en un nouveau
3. Activez l'API Google Calendar :
   - Allez dans "APIs & Services" > "Library"
   - Recherchez "Google Calendar API"
   - Cliquez sur "Enable"

4. Créez un Service Account :
   - Allez dans "APIs & Services" > "Credentials"
   - Cliquez sur "Create Credentials" > "Service Account"
   - Donnez un nom au service account (ex: "absence-calendar-sync")
   - Cliquez sur "Create and Continue"
   - Assignez le rôle "Editor" ou créez un rôle personnalisé avec les permissions Calendar
   - Cliquez sur "Done"

### 2. Générer les credentials JSON

1. Dans la liste des Service Accounts, cliquez sur celui que vous venez de créer
2. Allez dans l'onglet "Keys"
3. Cliquez sur "Add Key" > "Create new key"
4. Sélectionnez "JSON" et cliquez sur "Create"
5. Le fichier JSON sera téléchargé automatiquement

### 3. Partager le calendrier avec le Service Account

1. Ouvrez Google Calendar
2. Dans la liste des calendriers à gauche, trouvez le calendrier `hello.obvious@gmail.com`
3. Cliquez sur les trois points à côté du calendrier > "Settings and sharing"
4. Dans la section "Share with specific people", cliquez sur "Add people"
5. Ajoutez l'email du service account (visible dans le fichier JSON sous `client_email`)
6. Donnez les permissions "Make changes to events"
7. Cliquez sur "Send"

### 4. Configurer les variables d'environnement

1. Ouvrez le fichier JSON téléchargé
2. Copiez tout le contenu du fichier
3. Dans votre fichier `.env`, ajoutez :
   ```
   GOOGLE_CALENDAR_CREDENTIALS={"type":"service_account","project_id":"..."}
   ```
   (remplacez par le contenu complet du fichier JSON sur une seule ligne)

### 5. Redémarrer l'application

Redémarrez votre application pour que les nouvelles variables d'environnement soient prises en compte.

## Fonctionnalités

Une fois configuré, le système :

- **Crée automatiquement** un événement dans Google Calendar quand une demande d'absence est approuvée
- **Met à jour** l'événement si la demande approuvée est modifiée
- **Supprime** l'événement si la demande est refusée ou supprimée
- **Affiche** le nom de l'employé et le type d'absence dans le calendrier
- **Utilise des couleurs** différentes pour les vacances (bleu) et la maladie (rouge)

## Format des événements

Les événements créés dans Google Calendar auront :
- **Titre** : `[Type d'absence] - [Nom Prénom]` (ex: "Vacances - Pierre Dupont")
- **Description** : Détails complets de la demande
- **Dates** : Événements de toute la journée sur la période demandée
- **Couleur** : Bleu pour les vacances, rouge pour la maladie

## Dépannage

### Le service ne fonctionne pas
- Vérifiez que la variable `GOOGLE_CALENDAR_CREDENTIALS` est correctement définie
- Vérifiez que l'API Google Calendar est activée dans votre projet
- Vérifiez que le service account a accès au calendrier

### Les événements ne sont pas créés
- Vérifiez les logs de l'application pour voir les erreurs
- Vérifiez que le calendrier `hello.obvious@gmail.com` existe et est accessible
- Vérifiez que les permissions du service account sont correctes

### Logs d'erreur
Les erreurs sont loggées dans les logs de l'application avec le préfixe `GoogleCalendarService`.