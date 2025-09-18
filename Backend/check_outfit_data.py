#!/usr/bin/env python3
"""
Script to check what's actually stored in the outfit_history table
"""

import os
import psycopg2
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_outfit_data():
    """Check the outfit data in the database"""
    try:
        print("Connecting to database...")
        
        # Get database URL from environment
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            # Try to construct from individual components
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "123456")
            database = os.getenv("DB_NAME", "styra_wardrobe")
            
            DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
        # Get all outfit history entries
        cursor.execute("""
            SELECT id, worn_date, outfit_data, occasion, weather, location, created_at
            FROM outfit_history 
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} outfit history entries:")
        print("=" * 80)
        
        for row in rows:
            id, worn_date, outfit_data, occasion, weather, location, created_at = row
            print(f"ID: {id}")
            print(f"Date: {worn_date}")
            print(f"Occasion: {occasion}")
            print(f"Weather: {weather}")
            print(f"Location: {location}")
            print(f"Created: {created_at}")
            print(f"Outfit Data Type: {type(outfit_data)}")
            
            if outfit_data:
                if isinstance(outfit_data, str):
                    try:
                        parsed_data = json.loads(outfit_data)
                        print(f"Outfit Data (parsed): {json.dumps(parsed_data, indent=2)}")
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON: {e}")
                        print(f"Raw outfit data: {outfit_data}")
                else:
                    print(f"Outfit Data (dict): {json.dumps(outfit_data, indent=2, default=str)}")
            else:
                print("Outfit Data: None")
            
            print("-" * 80)
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_outfit_data()
