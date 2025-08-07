# Configuration Email

## Options disponibles

### 1. Resend (Recommandé) ⭐

**Avantages :**
- Plan gratuit : 3,000 emails/mois
- Pas besoin de mot de passe d'application
- API moderne et simple
- Meilleure délivrabilité
- Support des pièces jointes

**Configuration :**
```bash
RESEND_API_KEY=re_votre_cle_api_ici
RESEND_FROM_EMAIL=noreply@votre-domaine.com
```

Voir le guide complet : [RESEND_EMAIL_SETUP.md](RESEND_EMAIL_SETUP.md)

### 2. Gmail SMTP (Configuration existante)

Pour que le système d'envoi d'emails fonctionne (déclarations de maladie vers hello.obvious@gmail.com), vous devez configurer les variables d'environnement suivantes dans votre fichier `.env` :

```bash
# Configuration email Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
EMAIL_FROM=votre-email@gmail.com
```

## Configuration Gmail

1. **Activer la validation en 2 étapes** sur votre compte Gmail
2. **Générer un mot de passe d'application** :
   - Aller dans les paramètres Google Account
   - Sécurité > Validation en 2 étapes > Mots de passe des applications
   - Générer un mot de passe pour "Mail"
3. **Utiliser ce mot de passe** dans la variable `SMTP_PASSWORD`

## Test de configuration

Utilisez le script de test pour vérifier votre configuration :

```bash
python test_email.py
```

Ce script vous permettra de :
- Vérifier quelle configuration est active (Resend ou SMTP)
- Tester l'envoi d'emails simples
- Tester l'envoi d'emails avec pièces jointes

## Mode Développement

Si aucune configuration email n'est fournie, les emails ne seront pas envoyés mais l'application continuera de fonctionner normalement avec un message de log dans la console.

## Priorité de configuration

L'application utilise automatiquement :
1. **Resend** si `RESEND_API_KEY` est configuré
2. **SMTP Gmail** si les variables SMTP sont configurées
3. **Mode silencieux** si aucune configuration n'est trouvée