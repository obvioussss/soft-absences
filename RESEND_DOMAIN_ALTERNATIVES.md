# Alternatives à Freenom pour Domaines Gratuits

## 🎯 Objectif

Obtenir un domaine gratuit ou à bas coût pour configurer Resend et pouvoir envoyer des emails à tous les utilisateurs.

## 🆓 Domaines Gratuits

### 1. **InfinityFree** (Recommandé)
- **URL** : [infinityfree.net](https://infinityfree.net)
- **Domaines** : `.epizy.com`, `.rf.gd`, `.rf.gd`
- **Avantages** : Gratuit, fiable, support DNS complet
- **Processus** :
  1. Créer un compte gratuit
  2. Choisir un sous-domaine (ex: `soft-absences.epizy.com`)
  3. Configurer les DNS dans le panneau de contrôle

### 2. **000webhost**
- **URL** : [000webhost.com](https://000webhost.com)
- **Domaines** : `.000webhostapp.com`
- **Avantages** : Gratuit, hébergement inclus
- **Processus** : Similaire à InfinityFree

### 3. **Netlify**
- **URL** : [netlify.com](https://netlify.com)
- **Domaines** : `.netlify.app`
- **Avantages** : Très fiable, gratuit
- **Processus** :
  1. Créer un compte
  2. Créer un site (peut être vide)
  3. Utiliser le domaine `.netlify.app`

## 💰 Domaines à Bas Coût

### 1. **Namecheap** (Recommandé)
- **URL** : [namecheap.com](https://namecheap.com)
- **Prix** : ~1€/an pour `.xyz`, ~10€/an pour `.com`
- **Avantages** : Très fiable, support excellent
- **Processus** :
  1. Rechercher un domaine disponible
  2. Acheter (paiement annuel)
  3. Configurer les DNS

### 2. **GoDaddy**
- **URL** : [godaddy.com](https://godaddy.com)
- **Prix** : ~10€/an pour `.com`
- **Avantages** : Très connu, fiable
- **Inconvénients** : Plus cher après la première année

### 3. **OVH**
- **URL** : [ovh.com](https://ovh.com)
- **Prix** : ~5€/an pour `.com`
- **Avantages** : Français, bon rapport qualité/prix

## 🚀 Solution Rapide : InfinityFree

### Étape 1 : Créer un compte
1. Aller sur [infinityfree.net](https://infinityfree.net)
2. Cliquer sur "Sign Up"
3. Remplir le formulaire
4. Confirmer l'email

### Étape 2 : Créer un domaine
1. Se connecter au panneau de contrôle
2. Aller dans "Domains" > "Add Domain"
3. Choisir un nom (ex: `soft-absences`)
4. Sélectionner `.epizy.com`
5. Créer le domaine

### Étape 3 : Configurer les DNS
1. Aller dans "DNS Manager"
2. Ajouter les enregistrements fournis par Resend :
   ```
   Type: TXT
   Name: @
   Value: v=spf1 include:_spf.resend.com ~all
   
   Type: TXT
   Name: resend._domainkey
   Value: [valeur fournie par Resend]
   ```

### Étape 4 : Vérifier sur Resend
1. Aller sur [resend.com/domains](https://resend.com/domains)
2. Cliquer "Add Domain"
3. Entrer `soft-absences.epizy.com`
4. Suivre les instructions de vérification

## 🔧 Configuration après obtention du domaine

### 1. Mettre à jour .env
```bash
RESEND_FROM_EMAIL=noreply@votre-domaine.com
```

### 2. Tester la configuration
```bash
python3 test_resend_domain.py
```

## 📊 Comparaison des options

| Option | Coût | Fiabilité | Facilité | Recommandation |
|--------|------|-----------|----------|----------------|
| InfinityFree | Gratuit | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ Recommandé |
| Namecheap | ~1-10€/an | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Excellent |
| Netlify | Gratuit | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ Bon |
| 000webhost | Gratuit | ⭐⭐⭐ | ⭐⭐⭐ | ⚠️ Moyen |

## 🎯 Recommandation finale

**Pour un test rapide** : InfinityFree avec `.epizy.com`
**Pour la production** : Namecheap avec `.com` ou `.xyz`

## 🆘 Besoin d'aide ?

Si vous choisissez InfinityFree, je peux vous guider étape par étape pour :
- Créer le compte
- Configurer le domaine
- Ajouter les enregistrements DNS
- Vérifier sur Resend

Quelle option préférez-vous ? 