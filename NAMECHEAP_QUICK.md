# Solution Ultra-Simple : Namecheap

## 🎯 Pourquoi Namecheap ?

- ✅ **Ultra-simple** : 2 minutes de configuration
- ✅ **Très fiable** : Support excellent
- ✅ **Pas cher** : ~1€/an pour .xyz
- ✅ **Pas de limitations** : DNS complet
- ✅ **Support 24/7** : Chat en direct

## 🚀 Configuration en 2 minutes

### 1. Acheter un domaine
1. **Aller sur** [namecheap.com](https://namecheap.com)
2. **Rechercher** un domaine disponible (ex: `soft-absences.xyz`)
3. **Acheter** (~1€/an pour .xyz)
4. **Payer** (carte bancaire)

### 2. Configurer les DNS
1. **Aller dans** "Domain List" > votre domaine > "Manage"
2. **Cliquer** "Advanced DNS"
3. **Ajouter** les enregistrements :

**Enregistrement SPF :**
- **Type** : TXT Record
- **Host** : @
- **Value** : `v=spf1 include:_spf.resend.com ~all`

**Enregistrement DKIM (après étape 3) :**
- **Type** : TXT Record
- **Host** : `resend._domainkey`
- **Value** : [valeur de Resend]

### 3. Ajouter sur Resend
1. **Aller sur** [resend.com/domains](https://resend.com/domains)
2. **Ajouter** votre domaine
3. **Copier** la valeur DKIM
4. **Revenir** sur Namecheap pour ajouter l'enregistrement DKIM

### 4. Vérifier et tester
1. **Vérifier** sur Resend
2. **Mettre à jour** .env
3. **Tester** : `python3 test_resend_domain.py`

## 💰 Coûts

- **.xyz** : ~1€/an
- **.com** : ~10€/an
- **.net** : ~12€/an

## 🎯 Recommandation

**Pour un test rapide** : `.xyz` à 1€/an
**Pour la production** : `.com` à 10€/an

## 🆘 Voulez-vous essayer ?

Si vous voulez que je vous guide avec Namecheap, dites-moi et je créerai un script d'assistance !

**Quelle option préférez-vous ?**
- 🆓 **Netlify** (gratuit, 5 minutes)
- 💰 **Namecheap** (1€/an, 2 minutes) 