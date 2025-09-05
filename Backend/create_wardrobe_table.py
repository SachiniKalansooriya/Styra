#!/usr/bin/env python3
"""
Create wardrobe_items table if it doesn't exist
"""

import sys
from pathlib import Path

# Add Backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.connection import db

def create_wardrobe_items_table():
    """Create the wardrobe_items table"""
    try:
        # Check if table exists
        check_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'wardrobe_items'
        );
        """
        
        result = db.execute_query(check_query)
        table_exists = result[0]['exists'] if result else False
        
        if table_exists:
            print("✅ wardrobe_items table already exists")
            
            # Check if we need to add image_path column
            column_check = """
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'wardrobe_items' AND column_name = 'image_path';
            """
            column_result = db.execute_query(column_check)
            
            if not column_result:
                print("Adding image_path column...")
                alter_query = """
                ALTER TABLE wardrobe_items 
                ADD COLUMN IF NOT EXISTS image_path VARCHAR(500);
                """
                db.execute_query(alter_query, fetch=False)
                print("✅ image_path column added")
            
            return True
        
        print("Creating wardrobe_items table...")
        
        # Create the table with the exact structure we expect
        create_query = """
        CREATE TABLE wardrobe_items (
            id SERIAL PRIMARY KEY,
            user_id INTEGER DEFAULT 1,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            color VARCHAR(30),
            season VARCHAR(20) DEFAULT 'all',
            image_path VARCHAR(500),
            confidence DECIMAL(5,2),
            analysis_method VARCHAR(50),
            times_worn INTEGER DEFAULT 0,
            last_worn DATE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        db.execute_query(create_query, fetch=False)
        print("✅ wardrobe_items table created successfully")
        
        # Verify it was created
        verify_result = db.execute_query(check_query)
        if verify_result and verify_result[0]['exists']:
            print("✅ Table creation verified")
            return True
        else:
            print("❌ Table creation could not be verified")
            return False
            
    except Exception as e:
        print(f"❌ Error creating wardrobe_items table: {e}")
        return False

if __name__ == "__main__":
    success = create_wardrobe_items_table()
    if success:
        print("\n🎉 wardrobe_items table is ready!")
        print("You can now add items to your wardrobe!")
    else:
        print("\n❌ Failed to create wardrobe_items table")
        print("Please check your database connection and permissions")