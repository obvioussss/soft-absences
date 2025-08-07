# Configuration Email avec Resend

## Alternative à Gmail SMTP

Resend est un service moderne d'envoi d'emails qui offre :
- **Plan gratuit** : 3,000 emails/mois
- **API simple** et moderne
- **Pas besoin de mot de passe d'application** comme Gmail
- **Support des pièces jointes**
- **Livraison fiable**

## Configuration

### 1. Créer un compte Resend

1. Aller sur [resend.com](https://resend.com)
2. Créer un compte gratuit
3. Vérifier votre domaine ou utiliser un domaine Resend

### 2. Obtenir votre clé API

1. Dans le dashboard Resend, aller dans "API Keys"
2. Créer une nouvelle clé API
3. Copier la clé (commence par `re_`)

### 3. Configurer les variables d'environnement

Ajoutez ces variables dans votre fichier `.env` :

```bash
# Configuration Resend (recommandé)
RESEND_API_KEY=re_votre_cle_api_ici
RESEND_FROM_EMAIL=noreply@votre-domaine.com

# OU garder la configuration SMTP existante
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=votre-email@gmail.com
# SMTP_PASSWORD=votre-mot-de-passe-app
# EMAIL_FROM=votre-email@gmail.com
```

### 4. Vérifier votre domaine (optionnel mais recommandé)

Pour une meilleure délivrabilité :
1. Dans Resend, aller dans "Domains"
2. Ajouter votre domaine
3. Configurer les enregistrements DNS
4. Utiliser votre domaine dans `RESEND_FROM_EMAIL`

## Avantages par rapport à Gmail

✅ **Plus simple** : Pas besoin de mot de passe d'application  
✅ **Plus fiable** : Service dédié aux emails  
✅ **Meilleure délivrabilité** : Optimisé pour les emails transactionnels  
✅ **API moderne** : Plus facile à utiliser  
✅ **Gratuit** : 3,000 emails/mois  
✅ **Support des pièces jointes** : Parfait pour les certificats médicaux  

## Test

Une fois configuré, les emails seront automatiquement envoyés via Resend au lieu de Gmail.

### Mode de fallback

Si `RESEND_API_KEY` n'est pas configuré, l'application utilisera automatiquement la configuration SMTP existante.

## Migration depuis Gmail

1. Configurer Resend comme ci-dessus
2. Tester l'envoi d'un email
3. Supprimer les variables Gmail si tout fonctionne
4. L'application détectera automatiquement Resend et l'utilisera

## Support

- Documentation Resend : [resend.com/docs](https://resend.com/docs)
- Support gratuit inclus dans le plan gratuit 