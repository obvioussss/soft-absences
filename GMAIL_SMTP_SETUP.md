# Configuration Gmail SMTP temporaire

## Pourquoi cette configuration ?

Resend en mode test ne permet d'envoyer qu'à `hello.obvious@gmail.com`. Pour envoyer des emails à tous les utilisateurs (comme `fautrel.pierre@gmail.com`), nous devons utiliser Gmail SMTP temporairement.

## Configuration Gmail

### 1. Activer la validation en 2 étapes
1. Aller sur [myaccount.google.com](https://myaccount.google.com)
2. Sécurité > Validation en 2 étapes > Activer

### 2. Générer un mot de passe d'application
1. Aller dans Sécurité > Validation en 2 étapes > Mots de passe des applications
2. Sélectionner "Mail" ou "Autre (nom personnalisé)"
3. Copier le mot de passe généré (16 caractères)

### 3. Mettre à jour le fichier .env

Remplacez le contenu de votre fichier `.env` par :

```bash
# Base de données
DATABASE_URL=sqlite:///./absences.db
DATABASE_URL_TEST=sqlite:///./test_absences.db

# Sécurité
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuration Email - Gmail SMTP (Temporaire)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=hello.obvious@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app_ici
EMAIL_FROM=hello.obvious@gmail.com

# Configuration Email - Resend (Commenté temporairement)
# RESEND_API_KEY=re_LnLQBRsx_KijiXD8q6uXpwfh7y25RoYhn
# RESEND_FROM_EMAIL=onboarding@resend.dev

# Environnement
ENVIRONMENT=development
```

### 4. Tester la configuration

```bash
python3 test_email.py
```

## Avantages de cette solution

✅ **Envoi à tous les utilisateurs** : Plus de limitation Resend  
✅ **Configuration simple** : Gmail est fiable  
✅ **Notifications complètes** : Pierre recevra ses confirmations  
✅ **Temporaire** : Vous pourrez revenir à Resend plus tard  

## Retour à Resend (plus tard)

Une fois que vous aurez vérifié un domaine sur Resend :
1. Commenter les variables Gmail
2. Décommenter les variables Resend
3. Mettre à jour `RESEND_FROM_EMAIL` avec votre domaine vérifié

## Test

Après configuration, tous les utilisateurs recevront :
- ✅ Notifications de nouvelles demandes (admins)
- ✅ Confirmations d'approbation/refus (utilisateurs)
- ✅ Notifications de modifications
- ✅ Notifications de suppressions 