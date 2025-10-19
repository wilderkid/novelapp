#!/usr/bin/env python3
"""
Test script to check AI providers in the database
"""

from database import SessionLocal
from models import AIProvider, AIModel

def check_providers():
    """Check what AI providers exist in the database"""
    db = SessionLocal()
    try:
        # Get all providers (including those that are not system or project-specific)
        all_providers = db.query(AIProvider).all()
        
        print(f"Found {len(all_providers)} total providers:")
        for provider in all_providers:
            print(f"  - ID: {provider.id}, Name: {provider.name}, Is System: {provider.is_system}")
            
            # Get models for this provider
            models = db.query(AIModel).filter(AIModel.provider_id == provider.id).all()
            print(f"    Models ({len(models)}):")
            for model in models:
                print(f"      - ID: {model.id}, Name: {model.name}, Identifier: {model.model_identifier}")
        
        print("\nAll available providers:")
        all_providers = db.query(AIProvider).all()
        for provider in all_providers:
            print(f"  - ID: {provider.id}, Name: {provider.name}")
            
    except Exception as e:
        print(f"Error checking providers: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    check_providers()