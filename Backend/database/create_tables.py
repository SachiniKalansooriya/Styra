# Backend/app/database/create_tables.py
"""
Script to create all database tables
Run this once to set up your database schema
"""

from models.all_models import Base
from database.database import engine

def create_all_tables():
    """Create all tables defined in the models"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Print all created tables
        print("\n📋 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    create_all_tables()