#!/usr/bin/env python3
"""
Fix the AI provider schema issue by making project_id nullable
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_schema():
    """Fix the database schema to allow nullable project_id"""
    try:
        # Get database connection info
        db_name = os.getenv('DB_NAME', 'storyforge')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '123456')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        
        print(f"Connecting to database: {db_host}:{db_port}/{db_name}")
        
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        
        print("Connected to database successfully")
        
        cursor = conn.cursor()
        
        # Make project_id nullable in ai_providers table
        print("Making project_id nullable in ai_providers table...")
        try:
            cursor.execute("ALTER TABLE ai_providers ALTER COLUMN project_id DROP NOT NULL;")
            print("Success: Modified ai_providers.project_id to be nullable")
        except psycopg2.Error as e:
            print(f"Note: Could not modify ai_providers.project_id (may already be nullable): {e}")
        
        # Also make project_id nullable in prompt_templates table for consistency
        print("Making project_id nullable in prompt_templates table...")
        try:
            cursor.execute("ALTER TABLE prompt_templates ALTER COLUMN project_id DROP NOT NULL;")
            print("Success: Modified prompt_templates.project_id to be nullable")
        except psycopg2.Error as e:
            print(f"Note: Could not modify prompt_templates.project_id (may already be nullable): {e}")
        
        # Commit changes
        conn.commit()
        
        cursor.close()
        conn.close()
        
        print("Database schema fix completed!")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return

if __name__ == "__main__":
    fix_schema()