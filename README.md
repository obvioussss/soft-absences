# 🏢 Logiciel de Gestion des Absences

Un système simple et efficace pour gérer les absences des employés avec deux types de comptes (admin et utilisateur).

## ✨ Fonctionnalités

### Pour les utilisateurs :
- 📝 Demander des congés (vacances, maladie, télétravail, congés sans solde)
- 👀 Voir ses demandes et leur statut
- ✏️ Modifier ses demandes en attente
- 🗑️ Supprimer ses demandes

### Pour les administrateurs :
- ✅ Approuver ou refuser les demandes d'absence
- 👥 Gérer les utilisateurs (créer, modifier, supprimer)
- 📊 Voir toutes les demandes d'absence
- 📅 Calendrier des absences approuvées
- 📧 Notifications email automatiques

## 🛠️ Technologies utilisées

- **Backend** : Python 3.9+ avec FastAPI
- **Frontend** : HTML5, CSS3, JavaScript (vanilla)
- **Base de données** : SQLite (développement), PostgreSQL (production)
- **Authentification** : JWT avec bcrypt
- **Tests** : pytest
- **Déploiement** : Vercel

## 🚀 Installation et utilisation

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation

1. **Cloner le projet**
   ```bash
   git clone <votre-repo>
   cd soft_abscences
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer le serveur de développement**
   ```bash
   python run_dev.py
   ```

   Le script va :
   - Créer automatiquement le fichier `.env`
   - Initialiser la base de données
   - Créer un compte administrateur par défaut
   - Lancer le serveur sur http://localhost:8000

### Compte administrateur par défaut

- **Email** : `admin@example.com`
- **Mot de passe** : `admin123`

⚠️ **Changez ce mot de passe après la première connexion !**

## 📱 Accès à l'application

- **API** : http://localhost:8000
- **Interface web** : http://localhost:8000/static/index.html
- **Documentation API** : http://localhost:8000/docs
- **Monitoring** : http://localhost:8000/redoc

## 🧪 Tests

Lancer tous les tests :
```bash
pytest
```

Lancer les tests avec couverture :
```bash
pytest --cov=app
```

## 📧 Configuration email (optionnel)

Pour activer les notifications email, modifiez le fichier `.env` :

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
EMAIL_FROM=votre-email@gmail.com
```

Pour Gmail, utilisez un mot de passe d'application (App Password).

## 🗃️ Structure du projet

```
soft_abscences/
├── app/                    # Code de l'application
│   ├── main.py            # Point d'entrée FastAPI
│   ├── models.py          # Modèles de base de données
│   ├── schemas.py         # Schémas Pydantic
│   ├── crud.py            # Opérations CRUD
│   ├── auth.py            # Authentification
│   ├── database.py        # Configuration DB
│   └── email_service.py   # Service d'email
├── static/                 # Interface web
│   ├── index.html         # Page principale
│   └── app.js             # Logique frontend
├── tests/                  # Tests
├── create_admin.py         # Script création admin
├── run_dev.py             # Script de développement
├── requirements.txt       # Dépendances Python
└── README.md              # Documentation
```

## 📊 API Endpoints

### Authentification
- `POST /token` - Connexion
- `GET /users/me` - Profil utilisateur connecté

### Utilisateurs (Admin uniquement)
- `GET /users/` - Liste des utilisateurs
- `POST /users/` - Créer un utilisateur
- `GET /users/{id}` - Détails d'un utilisateur
- `PUT /users/{id}` - Modifier un utilisateur
- `DELETE /users/{id}` - Supprimer un utilisateur

### Demandes d'absence
- `GET /absence-requests/` - Mes demandes (utilisateur) / Toutes (admin)
- `POST /absence-requests/` - Créer une demande
- `GET /absence-requests/{id}` - Détails d'une demande
- `PUT /absence-requests/{id}` - Modifier une demande
- `PUT /absence-requests/{id}/status` - Changer le statut (admin)
- `DELETE /absence-requests/{id}` - Supprimer une demande

### Calendrier
- `GET /calendar/events` - Événements du calendrier

## 🚢 Déploiement

### Déploiement local pour production

1. Créer un fichier `.env` de production
2. Configurer une base de données PostgreSQL
3. Lancer avec gunicorn :
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Déploiement sur Vercel

Le projet est configuré pour être déployé sur Vercel. Un fichier `vercel.json` est fourni.

## 🐛 Dépannage

### Problèmes courants

1. **Erreur de base de données**
   - Supprimez le fichier `absences.db` et relancez `python run_dev.py`

2. **Erreur d'import**
   - Vérifiez que vous êtes dans le bon répertoire
   - Réinstallez les dépendances : `pip install -r requirements.txt`

3. **Erreur de port occupé**
   - Changez le port dans `run_dev.py` ou tuez le processus qui utilise le port 8000

## 🤝 Contribution

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème, ouvrez une issue sur GitHub.