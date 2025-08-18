# 📅 Configuration Google Calendar

Ce guide vous explique comment configurer la synchronisation avec Google Calendar pour voir les absences des employés directement dans votre calendrier Google.

## 🎯 Fonctionnalités

Une fois configuré, le système synchronisera automatiquement :
- ✅ **Demandes d'absence** (vacances et maladie) avec différents statuts
- 🏥 **Déclarations de maladie** avec indicateurs d'email
- 🎨 **Codes couleur** selon le statut (en attente = jaune, approuvé = vert, refusé = rouge)
- 🔄 **Synchronisation bidirectionnelle** : créer, modifier, supprimer

## 📋 Prérequis

1. Un compte Google avec accès à Google Calendar
2. Un projet Google Cloud Platform (gratuit)
3. Accès administrateur à votre calendrier Google

## 🛠️ Configuration étape par étape

### Étape 1 : Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Cliquez sur "Créer un projet" ou sélectionnez un projet existant
3. Notez l'ID de votre projet

### Étape 2 : Activer l'API Google Calendar

1. Dans le menu de gauche, allez dans **APIs & Services > Library**
2. Recherchez "Google Calendar API"
3. Cliquez sur "Google Calendar API" puis "ENABLE"

### Étape 3 : Créer un compte de service

1. Allez dans **APIs & Services > Credentials**
2. Cliquez sur **"+ CREATE CREDENTIALS" > "Service account"**
3. Remplissez les informations :
   - **Service account name** : `soft-absences-calendar`
   - **Service account ID** : `soft-absences-calendar` (généré automatiquement)
   - **Description** : `Service account pour synchroniser les absences avec Google Calendar`
4. Cliquez sur **"CREATE AND CONTINUE"**
5. Rôle : sélectionnez **"Editor"** ou laissez vide
6. Cliquez sur **"DONE"**

### Étape 4 : Générer la clé du service account

1. Dans la liste des comptes de service, cliquez sur le compte que vous venez de créer
2. Allez dans l'onglet **"KEYS"**
3. Cliquez sur **"ADD KEY" > "Create new key"**
4. Sélectionnez **"JSON"** et cliquez sur **"CREATE"**
5. Le fichier JSON est téléchargé automatiquement - **gardez-le précieusement !**

### Étape 5 : Partager votre calendrier avec le service account

1. Ouvrez [Google Calendar](https://calendar.google.com/)
2. Dans la liste des calendriers à gauche, trouvez le calendrier que vous voulez utiliser
3. Cliquez sur les trois points à côté du nom du calendrier > **"Paramètres et partage"**
4. Dans la section **"Partager avec des personnes spécifiques"**, cliquez sur **"+ Ajouter des personnes"**
5. Ajoutez l'email du service account (se trouve dans le fichier JSON téléchargé, champ `client_email`)
6. Accordez les permissions **"Apporter des modifications aux événements"**
7. Cliquez sur **"Envoyer"**

### Étape 6 : Obtenir l'ID du calendrier

1. Toujours dans les paramètres du calendrier
2. Faites défiler jusqu'à **"Intégrer le calendrier"**
3. Copiez l'**"ID du calendrier"** (format : `xxxxxx@group.calendar.google.com`)
4. Si vous voulez utiliser votre calendrier principal, utilisez `primary`

### Étape 7 : Encoder les credentials en base64

Ouvrez un terminal et exécutez :

```bash
# Remplacez "path/to/your/service-account.json" par le chemin vers votre fichier
base64 -i path/to/your/service-account.json
```

Copiez la longue chaîne de caractères générée.

### Étape 8 : Configurer les variables d'environnement

Ajoutez ces variables à votre fichier `.env.production` :

```env
# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS=votre-chaîne-base64-ici
GOOGLE_CALENDAR_ID=votre-id-calendrier-ou-primary
```

### Étape 9 : Déployer les changements

1. Commitez et poussez vos changements sur GitHub
2. Vercel déploiera automatiquement avec la nouvelle configuration
3. Ou utilisez le script de déploiement : `./deploy.sh`

### Étape 10 : Synchroniser les absences existantes

Exécutez le script de synchronisation pour les absences déjà présentes :

```bash
python3 sync_existing_absences.py
```

## 🎨 Codes couleur des événements

- 🟡 **Jaune** : Demandes en attente
- 🟢 **Vert** : Demandes approuvées
- 🔴 **Rouge** : Demandes refusées ou arrêts maladie

## 📱 Utilisation

Une fois configuré, tous les événements d'absence apparaîtront automatiquement dans votre calendrier Google :

### Format des événements d'absence :
```
✅ Jean Dupont - Vacances
⏳ Marie Martin - Maladie (En attente)
❌ Pierre Durand - Vacances (Refusé)
```

### Format des déclarations de maladie :
```
🏥 Sophie Bernard - Arrêt maladie ✉️
🏥 Thomas Petit - Arrêt maladie ❌
```

## 🔧 Dépannage

### Erreur "Calendar not found"
- Vérifiez que l'ID du calendrier est correct
- Assurez-vous que le service account a bien été ajouté au calendrier

### Erreur "Permission denied"
- Vérifiez que le service account a les permissions d'écriture sur le calendrier
- Re-partagez le calendrier si nécessaire

### Erreur "Invalid credentials"
- Vérifiez que le JSON est correctement encodé en base64
- Assurez-vous qu'il n'y a pas d'espaces ou de retours à la ligne dans la variable

### Les événements n'apparaissent pas
- Vérifiez les logs de l'application
- Testez avec le script de synchronisation manuelle
- Vérifiez que l'API Google Calendar est bien activée

## 📞 Support

Si vous rencontrez des difficultés, vérifiez :
1. Les logs de l'application dans Vercel
2. Que toutes les variables d'environnement sont définies
3. Que l'API Google Calendar est activée
4. Que le service account a bien accès au calendrier

## 🔒 Sécurité

- Le fichier JSON du service account contient des informations sensibles
- Ne le commitez jamais dans votre repository Git
- Les credentials sont stockés de manière sécurisée dans les variables d'environnement Vercel
- Le service account n'a accès qu'au calendrier spécifique que vous avez partagé