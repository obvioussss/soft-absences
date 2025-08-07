# Notification Email pour Arrêts Maladie Marqués comme Vus

## Fonctionnalité Ajoutée

Quand un administrateur clique sur "Marquer vue" sur un arrêt maladie d'un utilisateur, un email est automatiquement envoyé à l'utilisateur pour l'informer.

## Implémentation

### 1. Service Email (`app/email_service.py`)

Nouvelle méthode ajoutée :
```python
def send_sickness_declaration_viewed_notification(self, user_email: str, user_name: str, start_date: str, end_date: str, admin_name: str):
    """Notifier l'utilisateur que son arrêt maladie a été marqué comme vu par l'admin"""
```

### 2. Routes (`app/routes/sickness_declarations.py`)

Deux routes modifiées pour envoyer l'email :

#### Route `mark_declaration_as_viewed`
- **Endpoint** : `POST /sickness-declarations/{declaration_id}/mark-viewed`
- **Action** : Marque la déclaration comme vue ET envoie un email à l'utilisateur
- **Retour** : `{"message": "Déclaration marquée comme vue et email envoyé"}`

#### Route `read_sickness_declaration`
- **Endpoint** : `GET /sickness-declarations/{declaration_id}`
- **Action** : Si un admin consulte une déclaration non vue, elle est automatiquement marquée comme vue ET un email est envoyé

### 3. Frontend (`static/js/sickness.js`)

La fonction `markSicknessAsViewed()` existe déjà et appelle la route appropriée.

## Contenu de l'Email

L'email contient :
- **Sujet** : "Arrêt maladie consulté - [Nom de l'utilisateur]"
- **Contenu** :
  - Salutation personnalisée
  - Information sur l'admin qui a consulté
  - Période de l'arrêt maladie
  - Confirmation que la déclaration a été marquée comme "vue"

## Exemple d'Email

```
Sujet : Arrêt maladie consulté - Jean Dupont

Bonjour Jean Dupont,

Votre arrêt maladie a été consulté par l'administrateur Admin Test :

Période : du 2024-01-15 au 2024-01-20

Votre déclaration a été marquée comme "vue" dans le système de gestion des absences.

Cordialement,
Système de gestion des absences
```

## Test

La fonctionnalité a été testée avec succès :
- ✅ Service email configuré (Resend)
- ✅ Méthode d'email fonctionnelle
- ✅ Routes modifiées correctement
- ✅ Frontend utilise la fonction appropriée

## Utilisation

1. L'admin se connecte à l'application
2. Il va dans la section "Déclarations de maladie"
3. Il clique sur le bouton "👁️ Marquer vue" à côté d'une déclaration
4. L'utilisateur reçoit automatiquement un email de notification
5. La déclaration est marquée comme "vue" dans le système 