#!/usr/bin/env python3
"""
Script to check the users table and see if signup data is being stored correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal, engine
from app.models.user import User
from sqlalchemy import text

def check_users_table():
    """Check the users table structure and data"""
    try:
        # Get database session
        db = SessionLocal()
        
        print("=== USERS TABLE ANALYSIS ===")
        
        # Check if users table exists
        result = db.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='users')"))
        table_exists = result.scalar()
        print(f"Users table exists: {table_exists}")
        
        if table_exists:
            # Check table structure
            print("\n--- Table Structure ---")
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """))
            columns = result.fetchall()
            
            for col in columns:
                print(f"Column: {col[0]} | Type: {col[1]} | Nullable: {col[2]} | Default: {col[3]}")
            
            # Check data in users table using SQLAlchemy
            print("\n--- Users Data ---")
            user_count = db.query(User).count()
            print(f"Total users in table: {user_count}")
            
            if user_count > 0:
                users = db.query(User).order_by(User.created_at.desc()).limit(10).all()
                print("\nRecent users:")
                for user in users:
                    print(f"ID: {user.id} | Username: {user.username} | Email: {user.email} | Full Name: {user.full_name} | Created: {user.created_at}")
            else:
                print("No users found in the table")
                
        else:
            print("Users table does not exist!")
            
            # Check what tables do exist
            print("\n--- Available Tables ---")
            result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = result.fetchall()
            for table in tables:
                print(f"Table: {table[0]}")
        
        db.close()
        
    except Exception as e:
        print(f"Error checking users table: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_users_table()
