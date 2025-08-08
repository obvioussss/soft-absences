# 🚀 Plan de Déploiement - Soft Absences

## 📋 État actuel de l'application

### ✅ Ce qui fonctionne déjà
- Configuration Vercel existante (`vercel.json`)
- API handlers pour Vercel (`api/index.py`)
- Fichiers statiques embarqués (`api/static_files.py`)
- Base de données en mémoire pour production
- Structure complète de l'application

### ⚠️ Points d'attention
- Base de données SQLite en mémoire (données perdues à chaque redémarrage)
- Pas de stockage persistant pour les uploads
- Configuration d'environnement minimale

## 🎯 Stratégie de déploiement

### Option 1 : Déploiement Vercel (Recommandé - EXACTEMENT cette version)

**Avantages :**
- Configuration déjà en place
- Déploiement instantané
- Gratuit pour usage personnel
- Exactement la version actuelle

**Étapes :**

1. **Préparer le repository**
   ```bash
   # Vérifier que tous les fichiers sont commités
   git add .
   git commit -m "Version prête pour déploiement"
   git push origin main
   ```

2. **Déployer sur Vercel**
   - Aller sur [vercel.com](https://vercel.com)
   - Connecter le repository GitHub
   - Vercel détectera automatiquement la configuration
   - Déploiement automatique

3. **Configuration des variables d'environnement**
   ```env
   ENVIRONMENT=production
   SECRET_KEY=votre-clé-secrète-sécurisée
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Option 2 : Déploiement avec base de données persistante

**Pour une solution plus robuste :**

1. **Base de données externe** (PostgreSQL sur Railway/Neon)
2. **Stockage fichiers** (AWS S3 ou similaire)
3. **Variables d'environnement complètes**

## 🔧 Configuration requise

### Variables d'environnement minimales
```env
# Obligatoires
ENVIRONMENT=production
SECRET_KEY=votre-clé-secrète-très-sécurisée

# Optionnelles (pour emails)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app

# Google Calendar (optionnel)
(Supprimé) GOOGLE_CALENDAR_CREDENTIALS=votre-credentials-json
```

### Fichiers de configuration
- `vercel.json` ✅ (déjà configuré)
- `requirements.txt` ✅ (déjà configuré)
- `api/index.py` ✅ (déjà configuré)

## 🚀 Instructions de déploiement

### Étape 1 : Préparation
```bash
# 1. Vérifier que tout fonctionne localement
python run_dev.py

# 2. Tester l'API
curl http://localhost:8000/health

# 3. Commiter les changements
git add .
git commit -m "Version finale pour déploiement"
git push origin main
```

### Étape 2 : Déploiement Vercel
1. Aller sur [vercel.com](https://vercel.com)
2. Se connecter avec GitHub
3. Importer le repository `soft_abscences`
4. Vercel détectera automatiquement la configuration
5. Cliquer sur "Deploy"

### Étape 3 : Configuration post-déploiement
1. Dans le dashboard Vercel, aller dans "Settings" > "Environment Variables"
2. Ajouter les variables d'environnement :
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = `votre-clé-secrète-sécurisée`

### Étape 4 : Test du déploiement
1. Tester l'URL de déploiement
2. Vérifier que l'authentification fonctionne
3. Tester les fonctionnalités principales

## 📊 Monitoring et maintenance

### URLs importantes
- **Application** : `https://soft-abscences.vercel.app`
- **API Health** : `https://soft-abscences.vercel.app/health`
- **Dashboard Vercel** : Dashboard Vercel pour monitoring

### Points de surveillance
- Logs Vercel pour les erreurs
- Performance de l'application
- Utilisation des ressources

## 🔄 Mises à jour futures

### Pour déployer une nouvelle version
```bash
# 1. Faire les modifications
# 2. Tester localement
# 3. Commiter et pousser
git add .
git commit -m "Nouvelle version"
git push origin main

# 4. Vercel déploiera automatiquement
```

## ⚠️ Limitations actuelles

1. **Base de données** : Données perdues à chaque redémarrage
2. **Fichiers uploadés** : Pas de stockage persistant
3. **Sessions** : Pas de stockage de session persistant

## 🎯 Recommandation finale

**Déployer immédiatement sur Vercel** avec la configuration actuelle pour avoir exactement cette version en ligne, puis évaluer les besoins de persistance des données selon l'usage. 