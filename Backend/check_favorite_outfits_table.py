#!/usr/bin/env python3
"""
Script to check the favorite_outfits table structure and content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import db
import json

def check_table_structure():
    """Check if favorite_outfits table exists and its structure"""
    try:
        # Check if table exists
        check_table_query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'favorite_outfits'
        );
        """
        
        result = db.execute_query(check_table_query)
        table_exists = result[0]['exists'] if result else False
        
        print(f"Table 'favorite_outfits' exists: {table_exists}")
        
        if table_exists:
            # Get table structure
            structure_query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'favorite_outfits'
            ORDER BY ordinal_position;
            """
            
            columns = db.execute_query(structure_query)
            print("\nTable structure:")
            for col in columns:
                print(f"  {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        return table_exists
        
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return False

def check_table_content():
    """Check content of favorite_outfits table"""
    try:
        # Count total records
        count_query = "SELECT COUNT(*) as total FROM favorite_outfits;"
        count_result = db.execute_query(count_query)
        total_count = count_result[0]['total'] if count_result else 0
        
        print(f"\nTotal records in favorite_outfits: {total_count}")
        
        if total_count > 0:
            # Get recent records
            recent_query = """
            SELECT id, user_id, outfit_name, occasion, season, 
                   confidence_score, times_worn, is_active, created_at
            FROM favorite_outfits 
            ORDER BY created_at DESC 
            LIMIT 10;
            """
            
            recent_records = db.execute_query(recent_query)
            print("\nRecent favorite outfits:")
            for record in recent_records:
                print(f"  ID: {record['id']}, User: {record['user_id']}, Name: {record['outfit_name']}")
                print(f"    Occasion: {record['occasion']}, Active: {record['is_active']}")
                print(f"    Created: {record['created_at']}")
                print()
        
        # Check for user_id = 1 specifically
        user_query = """
        SELECT COUNT(*) as user_count 
        FROM favorite_outfits 
        WHERE user_id = 1 AND is_active = TRUE;
        """
        
        user_result = db.execute_query(user_query)
        user_count = user_result[0]['user_count'] if user_result else 0
        print(f"Active favorites for user_id = 1: {user_count}")
        
        if user_count > 0:
            # Get user's favorites
            user_favorites_query = """
            SELECT id, outfit_name, outfit_data, occasion, confidence_score, created_at
            FROM favorite_outfits 
            WHERE user_id = 1 AND is_active = TRUE
            ORDER BY created_at DESC;
            """
            
            user_favorites = db.execute_query(user_favorites_query)
            print("\nUser 1's favorites:")
            for fav in user_favorites:
                print(f"  {fav['outfit_name']} - {fav['occasion']} ({fav['confidence_score']}%)")
                # Try to parse outfit_data
                try:
                    outfit_items = json.loads(fav['outfit_data']) if fav['outfit_data'] else []
                    print(f"    Items: {len(outfit_items)} pieces")
                except json.JSONDecodeError:
                    print(f"    Items: Invalid JSON data")
                print()
        
    except Exception as e:
        print(f"Error checking table content: {e}")

def main():
    print("=== Checking favorite_outfits table ===")
    
    # Test database connection
    try:
        test_query = "SELECT 1 as test;"
        db.execute_query(test_query)
        print("Database connection: OK")
    except Exception as e:
        print(f"Database connection error: {e}")
        return
    
    # Check table structure
    table_exists = check_table_structure()
    
    if table_exists:
        # Check table content
        check_table_content()
    else:
        print("Table does not exist. Creating it...")
        try:
            from services.favorite_outfit_service import favorite_outfit_service
            print("Table created successfully!")
            check_table_content()
        except Exception as e:
            print(f"Error creating table: {e}")

if __name__ == "__main__":
    main()
