#!/usr/bin/env python3
"""
Check the current API key in the database
"""

from database import SessionLocal
from models import AIProvider

def check_api_key():
    """Check the API key in the database"""
    db = SessionLocal()
    try:
        # Get the OpenAI provider (ID 1 based on our test)
        provider = db.query(AIProvider).filter(AIProvider.id == 1).first()
        
        if provider:
            print(f"Provider ID: {provider.id}")
            print(f"Provider Name: {provider.name}")
            print(f"Current API Key: {provider.api_key[:10]}...{provider.api_key[-5:] if len(provider.api_key) > 15 else provider.api_key} (showing first 10 and last 5 chars)")
            print(f"API Key Length: {len(provider.api_key)}")
            print(f"Base URL: {provider.base_url}")
        else:
            print("No provider found with ID 1")
            
    except Exception as e:
        print(f"Error checking API key: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    check_api_key()