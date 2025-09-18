#!/usr/bin/env python3
"""
Script to update the outfit_history table schema
"""

import sys
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_outfit_history_table():
    """Update the outfit_history table to add any missing columns"""
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
            print(f"Constructed DATABASE_URL from components")
        
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Connected to database successfully!")
        
        # Check if the weather column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='outfit_history' AND column_name='weather'
            );
        """)
        weather_exists = cursor.fetchone()[0]
        
        # Check if the location column exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name='outfit_history' AND column_name='location'
            );
        """)
        location_exists = cursor.fetchone()[0]
        
        print(f"Weather column exists: {weather_exists}")
        print(f"Location column exists: {location_exists}")
        
        # Add weather column if it doesn't exist
        if not weather_exists:
            print("Adding 'weather' column to outfit_history table...")
            cursor.execute("""
                ALTER TABLE outfit_history 
                ADD COLUMN weather VARCHAR(255);
            """)
            print("'weather' column added successfully.")
        else:
            print("'weather' column already exists.")
        
        # Add location column if it doesn't exist
        if not location_exists:
            print("Adding 'location' column to outfit_history table...")
            cursor.execute("""
                ALTER TABLE outfit_history 
                ADD COLUMN location VARCHAR(255);
            """)
            print("'location' column added successfully.")
        else:
            print("'location' column already exists.")
            
        # Commit the changes
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Outfit history table update completed successfully.")
        return True
        
    except Exception as e:
        print(f"Database error: {e}")
        print(f"Error updating outfit_history table: {e}")
        return False

if __name__ == "__main__":
    print("Starting outfit_history table update...")
    success = update_outfit_history_table()
    if success:
        print("Update completed successfully!")
    else:
        print("Update failed!")
