#!/bin/bash

# 🚀 Script de déploiement - Soft Absences
# Ce script automatise le processus de déploiement sur Vercel

set -e  # Arrêter le script en cas d'erreur

echo "🚀 Démarrage du processus de déploiement..."

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que git est installé
if ! command -v git &> /dev/null; then
    print_error "Git n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier que nous sommes dans un repository git
if [ ! -d ".git" ]; then
    print_error "Ce répertoire n'est pas un repository git."
    exit 1
fi

# Vérifier le statut git
print_message "Vérification du statut git..."
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Il y a des modifications non commitées."
    echo "Modifications détectées :"
    git status --short
    
    read -p "Voulez-vous commiter ces modifications ? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Message de commit: " commit_message
        if [ -z "$commit_message" ]; then
            commit_message="Déploiement automatique - $(date)"
        fi
        git add .
        git commit -m "$commit_message"
        print_success "Modifications commitées avec le message: $commit_message"
    else
        print_error "Déploiement annulé. Veuillez commiter vos modifications d'abord."
        exit 1
    fi
else
    print_success "Aucune modification non commitée détectée."
fi

# Vérifier que nous sommes sur la branche main
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_warning "Vous n'êtes pas sur la branche main (actuellement sur: $current_branch)"
    read -p "Voulez-vous basculer sur la branche main ? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        print_success "Basculé sur la branche main."
    else
        print_error "Déploiement annulé. Veuillez basculer sur la branche main d'abord."
        exit 1
    fi
fi

# Pousser les modifications
print_message "Poussage des modifications vers le repository distant..."
git push origin main
print_success "Modifications poussées avec succès."

# Vérifier que Vercel CLI est installé
if ! command -v vercel &> /dev/null; then
    print_warning "Vercel CLI n'est pas installé."
    echo "Pour installer Vercel CLI :"
    echo "npm install -g vercel"
    echo ""
    print_message "Vous pouvez maintenant déployer manuellement :"
    echo "1. Aller sur https://vercel.com"
    echo "2. Connecter votre repository GitHub"
    echo "3. Cliquer sur 'Deploy'"
else
    print_message "Vercel CLI détecté. Démarrage du déploiement..."
    
    # Vérifier si le projet est déjà configuré
    if [ -f ".vercel/project.json" ]; then
        print_message "Projet Vercel déjà configuré. Déploiement..."
        vercel --prod
    else
        print_message "Configuration initiale du projet Vercel..."
        vercel
    fi
fi

print_success "🎉 Déploiement terminé avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Vérifier que l'application fonctionne sur l'URL fournie"
echo "2. Configurer les variables d'environnement dans le dashboard Vercel :"
echo "   - ENVIRONMENT=production"
echo "   - SECRET_KEY=votre-clé-secrète-sécurisée"
echo "3. Tester l'authentification et les fonctionnalités principales"
echo ""
echo "🔗 URLs importantes :"
echo "- Application : https://soft-abscences.vercel.app"
echo "- Health check : https://soft-abscences.vercel.app/health"
echo ""
print_success "Déploiement réussi ! 🚀" 