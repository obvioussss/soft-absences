#!/usr/bin/env python3
"""
Script pour synchroniser les absences existantes avec Google Calendar
Ce script doit être exécuté une seule fois après l'installation de la fonctionnalité Google Calendar
"""
import os
import sys
from datetime import datetime

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models
from app.google_calendar_service import google_calendar_service

def sync_existing_absences():
    """Synchronise toutes les absences existantes avec Google Calendar"""
    
    if not google_calendar_service.is_configured():
        print("❌ Service Google Calendar non configuré. Veuillez configurer les variables d'environnement :")
        print("   - GOOGLE_CALENDAR_CREDENTIALS")
        print("   - GOOGLE_CALENDAR_ID")
        return False
    
    print("🔄 Synchronisation des absences existantes avec Google Calendar...")
    
    db = SessionLocal()
    try:
        # Synchroniser les demandes d'absence
        absence_requests = db.query(models.AbsenceRequest).filter(
            models.AbsenceRequest.google_calendar_event_id.is_(None)
        ).all()
        
        print(f"📋 Trouvé {len(absence_requests)} demandes d'absence à synchroniser")
        
        synced_absences = 0
        for request in absence_requests:
            try:
                event_id = google_calendar_service.create_event(request)
                if event_id:
                    request.google_calendar_event_id = event_id
                    synced_absences += 1
                    print(f"  ✅ Absence #{request.id} synchronisée (événement: {event_id})")
                else:
                    print(f"  ❌ Échec synchronisation absence #{request.id}")
            except Exception as e:
                print(f"  ❌ Erreur absence #{request.id}: {e}")
        
        # Synchroniser les déclarations de maladie
        sickness_declarations = db.query(models.SicknessDeclaration).filter(
            models.SicknessDeclaration.google_calendar_event_id.is_(None)
        ).all()
        
        print(f"📋 Trouvé {len(sickness_declarations)} déclarations de maladie à synchroniser")
        
        synced_sickness = 0
        for declaration in sickness_declarations:
            try:
                event_id = google_calendar_service.create_sickness_event(declaration)
                if event_id:
                    declaration.google_calendar_event_id = event_id
                    synced_sickness += 1
                    print(f"  ✅ Déclaration #{declaration.id} synchronisée (événement: {event_id})")
                else:
                    print(f"  ❌ Échec synchronisation déclaration #{declaration.id}")
            except Exception as e:
                print(f"  ❌ Erreur déclaration #{declaration.id}: {e}")
        
        # Sauvegarder les changements
        db.commit()
        
        print(f"\n🎉 Synchronisation terminée !")
        print(f"   - Absences synchronisées : {synced_absences}/{len(absence_requests)}")
        print(f"   - Déclarations synchronisées : {synced_sickness}/{len(sickness_declarations)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Point d'entrée du script"""
    print("🚀 Script de synchronisation Google Calendar")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    if not os.getenv('GOOGLE_CALENDAR_CREDENTIALS'):
        print("❌ Variable GOOGLE_CALENDAR_CREDENTIALS non définie")
        print("   Ajoutez cette variable à votre fichier .env ou .env.production")
        return
    
    if not os.getenv('GOOGLE_CALENDAR_ID'):
        print("❌ Variable GOOGLE_CALENDAR_ID non définie")
        print("   Ajoutez cette variable à votre fichier .env ou .env.production")
        return
    
    # Effectuer la synchronisation
    success = sync_existing_absences()
    
    if success:
        print("\n✅ Synchronisation réussie ! Toutes les absences sont maintenant visibles dans Google Calendar.")
    else:
        print("\n❌ La synchronisation a échoué. Vérifiez les logs ci-dessus pour plus de détails.")

if __name__ == "__main__":
    main()