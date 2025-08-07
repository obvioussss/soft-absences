# Configuration Netlify + Resend (Solution Simple)

## 🎯 Pourquoi Netlify ?

- ✅ **Gratuit** et fiable
- ✅ **Configuration DNS simple**
- ✅ **Pas de limitations** comme InfinityFree
- ✅ **Support complet** des enregistrements TXT
- ✅ **Processus automatisé**

## 📋 Étapes (5 minutes)

### 1. Créer un compte Netlify
1. **Aller sur** [netlify.com](https://netlify.com)
2. **Cliquer "Sign up"** (avec GitHub, Google, ou email)
3. **Créer un compte** gratuit

### 2. Créer un site (peut être vide)
1. **Cliquer "New site from Git"** ou **"Deploy manually"**
2. **Choisir "Deploy manually"**
3. **Glisser-déposer** n'importe quel fichier (ex: un fichier `index.html` vide)
4. **Attendre** le déploiement (30 secondes)

### 3. Obtenir votre domaine
1. **Aller dans** "Site settings" > "Domain management"
2. **Votre domaine** sera : `votre-site-123456.netlify.app`
3. **Copier** ce domaine

### 4. Configurer les DNS sur Netlify
1. **Aller dans** "Site settings" > "Domain management" > "DNS"
2. **Cliquer "Add DNS record"**
3. **Ajouter l'enregistrement SPF :**
   - **Type** : TXT
   - **Name** : @ (ou laissez vide)
   - **Value** : `v=spf1 include:_spf.resend.com ~all`

### 5. Ajouter le domaine sur Resend
1. **Aller sur** [resend.com/domains](https://resend.com/domains)
2. **Cliquer "Add Domain"**
3. **Entrer** votre domaine Netlify (ex: `votre-site-123456.netlify.app`)
4. **Suivre** les instructions de vérification

### 6. Ajouter l'enregistrement DKIM
1. **Copier** la valeur DKIM fournie par Resend
2. **Revenir sur Netlify** > "Site settings" > "Domain management" > "DNS"
3. **Ajouter l'enregistrement DKIM :**
   - **Type** : TXT
   - **Name** : `resend._domainkey`
   - **Value** : [valeur DKIM de Resend]

### 7. Vérifier sur Resend
1. **Revenir sur Resend**
2. **Cliquer "Verify"**
3. **Attendre** la vérification (5-10 minutes)

### 8. Mettre à jour votre application
```bash
RESEND_FROM_EMAIL=noreply@votre-site-123456.netlify.app
```

## ✅ Avantages Netlify

- 🚀 **Configuration en 5 minutes**
- 🆓 **100% gratuit**
- 🔒 **Très fiable**
- 📧 **Support complet** des enregistrements DNS
- 🎯 **Pas de limitations** comme InfinityFree

## 🆘 Besoin d'aide ?

Si vous voulez que je vous guide étape par étape avec Netlify, dites-moi et je créerai un script d'assistance spécifique !

**Voulez-vous essayer Netlify ?** 🚀 