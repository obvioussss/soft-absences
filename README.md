# 🏢 Gestion des Absences

Application web complète pour la gestion des absences et congés avec intégration Google Calendar.

## ✨ Fonctionnalités

### 🔐 Authentification
- Connexion sécurisée avec JWT
- Rôles utilisateur et administrateur
- Gestion des sessions

### 📋 Gestion des absences
- Demande d'absence (vacances/maladie)
- Approbation/rejet par les administrateurs
- Historique complet des demandes
- Calcul automatique des jours de congés

### 📅 Calendrier intégré
- Vue calendrier interactive
- Affichage des absences approuvées
- Vue mensuelle pour les administrateurs
- Vue annuelle pour les utilisateurs

### 🔗 Intégration Google Calendar
- Synchronisation automatique des absences approuvées
- Création/mise à jour/suppression d'événements
- Interface d'administration dédiée
- Couleurs distinctives (bleu pour vacances, rouge pour maladie)

### 📧 Notifications par email
- Notifications automatiques aux administrateurs
- Support SMTP et Resend
- Emails de confirmation

### 📄 Déclarations de maladie
- Upload de certificats médicaux (PDF)
- Gestion des déclarations par les administrateurs
- Notifications par email

### 👥 Gestion des utilisateurs
- Création/modification/suppression d'utilisateurs
- Attribution de rôles
- Gestion des congés annuels

## 🛠️ Technologies

- **Backend** : Python FastAPI
- **Base de données** : SQLite avec SQLAlchemy
- **Frontend** : HTML/CSS/JavaScript vanilla
- **Authentification** : JWT
- **Emails** : SMTP/Resend
- **Calendrier** : Google Calendar API
- **Déploiement** : Vercel/Netlify

## 🚀 Installation

### Prérequis
- Python 3.8+
- Git

### Installation locale

1. **Cloner le repository**
```bash
git clone <repository-url>
cd soft_abscences
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

4. **Initialiser la base de données**
```bash
python -m alembic upgrade head
```

5. **Créer un utilisateur administrateur**
```bash
python create_admin.py
```

6. **Lancer l'application**
```bash
python run_dev.py
```

L'application sera accessible sur `http://localhost:8000`

## 📁 Structure du projet

```
soft_abscences/
├── app/                    # Application FastAPI
│   ├── crud/              # Opérations base de données
│   ├── routes/            # Routes API
│   ├── models.py          # Modèles SQLAlchemy
│   ├── schemas.py         # Schémas Pydantic
│   └── main.py           # Point d'entrée
├── static/                # Frontend
│   ├── css/              # Styles
│   ├── js/               # JavaScript modulaire
│   └── templates/        # Templates HTML
├── tests/                # Tests unitaires
├── alembic/              # Migrations base de données
└── uploads/              # Fichiers uploadés
```

## 🔧 Configuration

### Variables d'environnement

```env
# Base de données
DATABASE_URL=sqlite:///./absences.db

# JWT
SECRET_KEY=votre-clé-secrète
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (SMTP ou Resend)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe
EMAIL_FROM=votre-email@gmail.com

# Ou pour Resend
RESEND_API_KEY=votre-clé-resend
RESEND_FROM_EMAIL=noreply@votre-domaine.com

# Google Calendar (optionnel)
GOOGLE_CALENDAR_CREDENTIALS={"type":"service_account",...}
```

### Configuration Google Calendar

1. Créer un projet Google Cloud
2. Activer l'API Google Calendar
3. Créer un service account
4. Télécharger le fichier JSON des credentials
5. Ajouter la variable `GOOGLE_CALENDAR_CREDENTIALS` dans `.env`

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app

# Tests spécifiques
pytest tests/test_auth.py
```

## 🚀 Déploiement

### Vercel (recommandé)

1. Connecter le repository GitHub à Vercel
2. Configurer les variables d'environnement
3. Déployer automatiquement

### Netlify

1. Connecter le repository GitHub à Netlify
2. Configurer le build command
3. Déployer

## 📊 Fonctionnalités avancées

### Calcul des congés
- Calcul automatique des jours ouvrés
- Gestion des congés annuels
- Historique des utilisations

### Interface d'administration
- Dashboard avec statistiques
- Gestion complète des utilisateurs
- Administration Google Calendar
- Gestion des déclarations de maladie

### Sécurité
- Authentification JWT
- Validation des données
- Protection CSRF
- Gestion des permissions

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT.

## 🔄 Historique des versions

### v1.0.0
- ✅ Refactoring complet du code
- ✅ Suppression des doublons
- ✅ Configuration centralisée
- ✅ Nettoyage des scripts obsolètes
- ✅ Documentation mise à jour
- ✅ Tests unitaires complets
- ✅ Intégration Google Calendar
- ✅ Gestion des déclarations de maladie