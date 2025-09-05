#!/usr/bin/env python3
"""Check wardrobe_items table structure"""

import sys
from pathlib import Path

# Add Backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.connection import db

try:
    result = db.execute_query("""
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'wardrobe_items' 
        ORDER BY ordinal_position;
    """)
    
    if result:
        print("Current wardrobe_items table structure:")
        for row in result:
            print(f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})")
    else:
        print("wardrobe_items table does not exist")
        
except Exception as e:
    print(f"Error: {e}")
