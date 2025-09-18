#!/usr/bin/env python3
"""
Script to recreate the users table with the correct SQLAlchemy structure
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal, engine
from app.models.user import User
from sqlalchemy import text

def recreate_users_table():
    """Drop and recreate the users table with correct structure"""
    try:
        # Get database session
        db = SessionLocal()
        
        print("=== RECREATING USERS TABLE ===")
        
        # Drop existing users table if it exists
        print("Dropping existing users table...")
        db.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        db.commit()
        
        # Create the new table using SQLAlchemy
        print("Creating new users table with SQLAlchemy...")
        User.__table__.create(engine)
        
        print("Users table recreated successfully!")
        
        # Verify the new structure
        print("\n--- New Table Structure ---")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = result.fetchall()
        
        for col in columns:
            print(f"Column: {col[0]} | Type: {col[1]} | Nullable: {col[2]} | Default: {col[3]}")
        
        db.close()
        
    except Exception as e:
        print(f"Error recreating users table: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    recreate_users_table()
