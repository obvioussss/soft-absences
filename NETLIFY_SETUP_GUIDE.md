# 🚀 Guide de configuration Netlify + Resend pour les emails

## 🎯 Objectif
Configurer un domaine personnalisé sur Netlify pour envoyer des emails aux utilisateurs via Resend.

## 📋 Prérequis
- ✅ Compte Netlify (déjà créé)
- ✅ Compte Resend avec clé API
- ✅ Fichier index.html (déjà présent)

## 🔧 Étapes de configuration

### 1. Déployer le site sur Netlify

1. **Aller sur** [app.netlify.com](https://app.netlify.com)
2. **Cliquer** "New site from Git" ou "Deploy manually"
3. **Choisir** "Deploy manually"
4. **Glisser-déposer** le fichier `index.html` dans la zone
5. **Attendre** le déploiement (30 secondes)
6. **Noter** le domaine généré (ex: `soft-absences-123456.netlify.app`)

### 2. Configurer les DNS sur Netlify

1. **Aller dans** "Site settings" (icône engrenage)
2. **Cliquer** "Domain management"
3. **Cliquer** "DNS"
4. **Cliquer** "Add DNS record"

#### Ajouter l'enregistrement SPF :
- **Type** : TXT
- **Name** : @ (ou laissez vide)
- **Value** : `v=spf1 include:_spf.resend.com ~all`
- **Cliquer** "Save"

### 3. Ajouter le domaine sur Resend

1. **Aller sur** [resend.com/domains](https://resend.com/domains)
2. **Cliquer** "Add Domain"
3. **Entrer** votre domaine Netlify (ex: `soft-absences-123456.netlify.app`)
4. **Cliquer** "Add Domain"
5. **Copier** la valeur DKIM fournie

### 4. Ajouter l'enregistrement DKIM

1. **Revenir sur** Netlify > "Site settings" > "Domain management" > "DNS"
2. **Cliquer** "Add DNS record"
3. **Ajouter l'enregistrement DKIM :**
   - **Type** : TXT
   - **Name** : `resend._domainkey`
   - **Value** : [valeur DKIM de Resend]
   - **Cliquer** "Save"

### 5. Vérifier le domaine

1. **Revenir sur** [resend.com/domains](https://resend.com/domains)
2. **Trouver** votre domaine dans la liste
3. **Cliquer** "Verify"
4. **Attendre** la vérification (5-10 minutes)
5. **Vérifier** que le statut passe à "Verified"

### 6. Mettre à jour la configuration

Une fois le domaine vérifié, mettre à jour le fichier `.env` :

```bash
# Remplacer la ligne RESEND_FROM_EMAIL par :
RESEND_FROM_EMAIL=noreply@votre-domaine-123456.netlify.app
```

### 7. Tester la configuration

```bash
python3 test_email.py
```

## ✅ Vérification finale

Après configuration, vous devriez avoir :
- ✅ Domaine Netlify déployé
- ✅ Enregistrements DNS configurés (SPF + DKIM)
- ✅ Domaine vérifié sur Resend
- ✅ Email d'expédition : `noreply@votre-domaine.netlify.app`
- ✅ Emails qui partent aux utilisateurs

## 🆘 En cas de problème

### Problème : Domaine non vérifié
- Vérifier que les enregistrements DNS sont corrects
- Attendre 10-15 minutes pour la propagation
- Vérifier la syntaxe des valeurs TXT

### Problème : Emails non envoyés
- Vérifier la clé API Resend
- Vérifier l'email d'expédition dans `.env`
- Tester avec `python3 test_email.py`

## 📞 Support

Si vous avez des questions, consultez :
- [Documentation Resend](https://resend.com/docs)
- [Documentation Netlify](https://docs.netlify.com)
- [Guide de configuration](NETLIFY_SETUP.md) 