# 🚀 Guide de Déploiement Rapide - Soft Absences

## 🎯 Déploiement en 5 minutes

### Prérequis
- ✅ Repository GitHub avec votre code
- ✅ Compte Vercel (gratuit)

---

## 📋 Étapes de déploiement

### 1. Préparer le repository
```bash
# Vérifier que tout est commité
git status

# Si des modifications, les commiter
git add .
git commit -m "Version prête pour déploiement"
git push origin main
```

### 2. Déployer sur Vercel

1. **Aller sur [vercel.com](https://vercel.com)**
2. **Se connecter avec GitHub**
3. **Cliquer sur "New Project"**
4. **Importer le repository `soft_abscences`**
5. **Vercel détectera automatiquement la configuration**
6. **Cliquer sur "Deploy"**

### 3. Configurer les variables d'environnement

Dans le dashboard Vercel de votre projet :

1. **Aller dans "Settings" > "Environment Variables"**
2. **Ajouter les variables suivantes :**

```env
ENVIRONMENT=production
SECRET_KEY=votre-clé-secrète-sécurisée
```

**Pour générer une clé secrète :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Tester le déploiement

1. **Vérifier l'URL de déploiement** (ex: `https://soft-abscences.vercel.app`)
2. **Tester l'endpoint de santé :** `https://soft-abscences.vercel.app/health`
3. **Tester l'authentification :**
   - Email: `admin@example.com`
   - Mot de passe: `password123`

---

## 🔧 Configuration avancée (optionnel)

### Variables d'environnement supplémentaires

```env
# Email (pour les notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS=votre-credentials-json

# CORS
CORS_ORIGINS=https://votre-domaine.com
```

### Configuration Gmail

1. **Aller dans les paramètres Google**
2. **Sécurité > Connexion à Google**
3. **Mots de passe d'application**
4. **Générer un mot de passe pour l'application**

---

## 🎯 URLs importantes

- **Application :** `https://soft-abscences.vercel.app`
- **Health check :** `https://soft-abscences.vercel.app/health`
- **Dashboard Vercel :** Dashboard Vercel pour monitoring

---

## ⚠️ Limitations actuelles

1. **Base de données :** Données perdues à chaque redémarrage (SQLite en mémoire)
2. **Fichiers uploadés :** Pas de stockage persistant
3. **Sessions :** Pas de stockage de session persistant

---

## 🔄 Mises à jour

Pour déployer une nouvelle version :

```bash
# 1. Faire les modifications
# 2. Commiter et pousser
git add .
git commit -m "Nouvelle version"
git push origin main

# 3. Vercel déploiera automatiquement
```

---

## 🆘 Dépannage

### Problème : Application ne se charge pas
- Vérifier les logs dans le dashboard Vercel
- Vérifier que les variables d'environnement sont configurées

### Problème : Authentification ne fonctionne pas
- Vérifier que `SECRET_KEY` est configurée
- Vérifier les logs d'erreur

### Problème : Emails ne s'envoient pas
- Vérifier la configuration SMTP
- Vérifier les credentials Gmail

---

## 📞 Support

Si vous rencontrez des problèmes :

1. **Vérifier les logs Vercel** dans le dashboard
2. **Tester localement** avec `python run_dev.py`
3. **Vérifier la configuration** des variables d'environnement

---

## 🎉 Félicitations !

Votre application est maintenant déployée et accessible en ligne ! 

**URL de votre application :** `https://soft-abscences.vercel.app` 