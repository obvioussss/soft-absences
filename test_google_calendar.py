#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration Google Calendar
"""
import os
import sys

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Tester que tous les imports fonctionnent"""
    print("🔄 Test des imports...")
    
    try:
        from app.google_calendar_service import google_calendar_service
        print("  ✅ google_calendar_service importé")
    except Exception as e:
        print(f"  ❌ Erreur import google_calendar_service: {e}")
        return False
    
    try:
        from app.routes.google_calendar import router
        print("  ✅ Routes Google Calendar importées")
    except Exception as e:
        print(f"  ❌ Erreur import routes Google Calendar: {e}")
        return False
    
    try:
        from app.main import app
        print("  ✅ Application FastAPI importée")
    except Exception as e:
        print(f"  ❌ Erreur import application: {e}")
        return False
    
    return True

def test_service_configuration():
    """Tester la configuration du service"""
    print("\n🔄 Test de la configuration du service...")
    
    try:
        from app.google_calendar_service import google_calendar_service
        
        is_configured = google_calendar_service.is_configured()
        
        if is_configured:
            print("  ✅ Service Google Calendar configuré et prêt")
            return True
        else:
            print("  ⚠️  Service Google Calendar non configuré (normal si pas encore configuré)")
            print("     Variables requises :")
            print("     - GOOGLE_CALENDAR_CREDENTIALS")
            print("     - GOOGLE_CALENDAR_ID")
            return True  # Ce n'est pas une erreur, juste pas configuré
    except Exception as e:
        print(f"  ❌ Erreur test configuration: {e}")
        return False

def test_database_models():
    """Tester que les modèles de base de données sont corrects"""
    print("\n🔄 Test des modèles de base de données...")
    
    try:
        from app import models
        
        # Vérifier que les champs google_calendar_event_id existent
        if hasattr(models.AbsenceRequest, 'google_calendar_event_id'):
            print("  ✅ Champ google_calendar_event_id présent dans AbsenceRequest")
        else:
            print("  ❌ Champ google_calendar_event_id manquant dans AbsenceRequest")
            return False
            
        if hasattr(models.SicknessDeclaration, 'google_calendar_event_id'):
            print("  ✅ Champ google_calendar_event_id présent dans SicknessDeclaration")
        else:
            print("  ❌ Champ google_calendar_event_id manquant dans SicknessDeclaration")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Erreur test modèles: {e}")
        return False

def test_routes_registration():
    """Tester que les routes sont bien enregistrées"""
    print("\n🔄 Test de l'enregistrement des routes...")
    
    try:
        from app.main import app
        
        # Vérifier que les routes Google Calendar sont enregistrées
        routes = [route.path for route in app.routes]
        
        google_calendar_routes = [route for route in routes if '/google-calendar' in route]
        
        if google_calendar_routes:
            print(f"  ✅ Routes Google Calendar trouvées : {google_calendar_routes}")
            return True
        else:
            print("  ❌ Aucune route Google Calendar trouvée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur test routes: {e}")
        return False

def main():
    """Fonction principale du script de test"""
    print("🚀 Test d'intégration Google Calendar")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration du service", test_service_configuration),
        ("Modèles de base de données", test_database_models),
        ("Enregistrement des routes", test_routes_registration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Résultats des tests :")
    print(f"  ✅ Réussis : {passed}")
    print(f"  ❌ Échoués : {failed}")
    
    if failed == 0:
        print("\n🎉 Tous les tests sont passés ! L'intégration Google Calendar est prête.")
        print("\nProchaines étapes :")
        print("1. Configurer les variables d'environnement GOOGLE_CALENDAR_CREDENTIALS et GOOGLE_CALENDAR_ID")
        print("2. Déployer l'application")
        print("3. Exécuter le script sync_existing_absences.py pour synchroniser les données existantes")
    else:
        print(f"\n❌ {failed} test(s) ont échoué. Veuillez corriger les erreurs avant de continuer.")

if __name__ == "__main__":
    main()