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
- **Déploiement** : Vercel

## 📁 Structure du projet

```
soft_abscences/
├── app/                    # Application FastAPI
│   ├── crud/              # Opérations base de données
│   │   ├── __init__.py
│   │   ├── absences.py
│   │   ├── calculations.py
│   │   ├── sickness.py
│   │   └── users.py
│   ├── routes/            # Routes API
│   │   ├── __init__.py
│   │   ├── absence_requests.py
│   │   ├── auth.py
│   │   ├── calendar.py
│   │   ├── dashboard.py
│   │   ├── sickness_declarations.py
│   │   └── users.py
│   ├── __init__.py
│   ├── auth.py            # Authentification JWT
│   ├── database.py        # Configuration base de données
│   ├── email_service.py   # Service d'envoi d'emails
│   ├── file_service.py    # Gestion des fichiers
│   ├── (supprimé) google_calendar_service.py
│   ├── main.py           # Point d'entrée FastAPI
│   ├── models.py         # Modèles SQLAlchemy
│   └── schemas.py        # Schémas Pydantic
├── api/                   # API pour Vercel
│   ├── database.py       # Base de données en mémoire
│   ├── handlers.py       # Gestionnaires de requêtes
│   ├── index.py          # Point d'entrée Vercel
│   └── static_files.py   # Fichiers statiques embarqués
├── static/               # Frontend
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── admin.js
│   │   ├── auth.js
│   │   ├── calendar.js
│   │   ├── config.js
│   │   ├── dashboard.js
│   │   ├── main.js
│   │   ├── sickness.js
│   │   └── utils.js
│   ├── (dashboard.html) [supprimé – SPA unique via index.html]
│   ├── index.html
│   └── style.css
├── tests/                # Tests unitaires
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_absence_requests.py
│   ├── test_auth.py
│   ├── test_calculations.py
│   ├── test_sickness_declarations.py
│   └── test_users.py
├── alembic/              # Migrations base de données
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── uploads/              # Fichiers uploadés
│   └── sickness_declarations/
├── .cursor/              # Configuration Cursor
├── .gitignore           # Fichiers ignorés par Git
├── alembic.ini          # Configuration Alembic
├── create_admin.py      # Script de création d'admin
├── pytest.ini          # Configuration pytest
├── README.md           # Documentation
├── requirements.txt    # Dépendances Python
├── run_dev.py         # Script de développement
└── vercel.json        # Configuration Vercel
```

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

# Google Calendar
(Supprimé) GOOGLE_CALENDAR_CREDENTIALS={"type":"service_account",...}

# CORS
CORS_ORIGINS=http://localhost:3000,https://votre-domaine.com
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ --cov=app --cov-report=html
```

## 🌐 Déploiement

### Vercel
1. Connectez votre repo GitHub à Vercel
2. Vercel détectera automatiquement la configuration
3. Configurez les variables d'environnement dans Vercel
4. Déployez !

## 📊 Fonctionnalités principales

- ✅ **Authentification complète** avec JWT
- ✅ **Gestion des utilisateurs** (CRUD)
- ✅ **Demandes d'absence** avec workflow d'approbation
- ✅ **Calendrier interactif** des absences
- ✅ **Intégration Google Calendar** automatique
- ✅ **Notifications email** (SMTP/Resend)
- ✅ **Déclarations de maladie** avec upload PDF
- ✅ **Interface web** complète et responsive
- ✅ **Tests automatisés** complets
- ✅ **API REST** documentée
- ✅ **Migrations de base de données** avec Alembic

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.