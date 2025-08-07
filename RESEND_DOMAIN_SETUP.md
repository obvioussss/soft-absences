# Configuration Domaine Resend

## 🎯 Objectif

Vérifier un domaine sur Resend pour pouvoir envoyer des emails à tous les utilisateurs (comme `fautrel.pierre@gmail.com`) au lieu d'être limité à `hello.obvious@gmail.com`.

## 📋 Étapes de configuration

### 1. Aller sur Resend Domains

1. **Connectez-vous** sur [resend.com](https://resend.com)
2. **Cliquez sur "Domains"** dans le menu de gauche
3. **Cliquez sur "Add Domain"**

### 2. Ajouter votre domaine

Vous avez plusieurs options :

#### Option A : Utiliser un domaine gratuit
- **Domaine suggéré** : `votre-app.com` ou `soft-absences.com`
- **Avantage** : Gratuit et professionnel
- **Inconvénient** : Nécessite un enregistrement de domaine

#### Option B : Utiliser un sous-domaine
- **Exemple** : `mail.votre-domaine.com`
- **Avantage** : Utilise votre domaine existant
- **Inconvénient** : Nécessite un domaine existant

#### Option C : Utiliser un service de domaine gratuit
- **Services** : Freenom, Namecheap, etc.
- **Coût** : ~10€/an pour un domaine .com

### 3. Configuration DNS

Une fois votre domaine ajouté, Resend vous donnera des enregistrements DNS à configurer :

#### Enregistrements à ajouter :

```dns
# Enregistrement SPF
Type: TXT
Name: @
Value: v=spf1 include:_spf.resend.com ~all

# Enregistrement DKIM
Type: TXT
Name: resend._domainkey
Value: [valeur fournie par Resend]

# Enregistrement MX (optionnel)
Type: MX
Name: @
Value: [valeur fournie par Resend]
```

### 4. Vérification

1. **Attendre 5-10 minutes** que les DNS se propagent
2. **Cliquer sur "Verify"** dans Resend
3. **Statut** : Doit passer de "Pending" à "Verified"

### 5. Mise à jour de la configuration

Une fois le domaine vérifié, mettez à jour votre `.env` :

```bash
# Configuration Email - Resend (avec domaine vérifié)
RESEND_API_KEY=re_LnLQBRsx_KijiXD8q6uXpwfh7y25RoYhn
RESEND_FROM_EMAIL=noreply@votre-domaine.com
```

## 🚀 Alternative rapide : Domaine gratuit

Si vous n'avez pas de domaine, voici une solution rapide :

### 1. Créer un domaine gratuit
- **Aller sur** [freenom.com](https://freenom.com)
- **Choisir** un domaine gratuit (.tk, .ml, .ga, etc.)
- **Exemple** : `soft-absences.tk`

### 2. Configurer les DNS
- **Aller dans** la gestion DNS de votre domaine
- **Ajouter** les enregistrements fournis par Resend

### 3. Vérifier sur Resend
- **Ajouter** le domaine dans Resend
- **Attendre** la vérification

## ✅ Test après configuration

Une fois le domaine vérifié :

```bash
python3 test_all_users.py
```

Vous devriez voir :
- ✅ **Pierre reçoit** ses notifications
- ✅ **Tous les utilisateurs** peuvent recevoir des emails
- ✅ **Plus de limitation** Resend

## 🔧 Dépannage

### Le domaine ne se vérifie pas
- **Attendre** 15-30 minutes pour la propagation DNS
- **Vérifier** que les enregistrements DNS sont corrects
- **Contacter** le support de votre registrar DNS

### Erreur d'envoi
- **Vérifier** que `RESEND_FROM_EMAIL` utilise votre domaine vérifié
- **Redémarrer** l'application après modification du `.env`

## 📧 Résultat final

Après configuration :
- ✅ **Envoi à tous les utilisateurs** : `fautrel.pierre@gmail.com`, etc.
- ✅ **Notifications complètes** : Approbations, refus, modifications
- ✅ **Configuration permanente** : Plus besoin de Gmail SMTP
- ✅ **Professionnel** : Emails depuis votre domaine

## 🆘 Besoin d'aide ?

Si vous avez des difficultés avec la configuration DNS, je peux vous aider avec :
- **Choix du domaine** : Recommandations selon votre budget
- **Configuration DNS** : Instructions détaillées pour votre registrar
- **Tests** : Vérification que tout fonctionne 