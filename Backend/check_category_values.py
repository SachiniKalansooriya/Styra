# check_category_values.py
from database.connection import db

def check_categories():
    """Check categories in the wardrobe_items table"""
    try:
        print("Testing database connection...")
        test_result = db.test_connection()
        print(f"Connection test result: {test_result}")
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'wardrobe_items'
                )
            """)
            table_exists = cursor.fetchone()[0]
            print(f"wardrobe_items table exists: {table_exists}")
            
            if not table_exists:
                print("Table doesn't exist! Can't continue.")
                return
            
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'wardrobe_items'
            """)
            
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  {col[0]}: {col[1]}")
            
            # Get distinct categories
            cursor.execute("SELECT DISTINCT category FROM wardrobe_items")
            categories = cursor.fetchall()
            
            print("\nCategories in database:", [c[0] for c in categories if c[0]])
            
            # Count items per category
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM wardrobe_items
                GROUP BY category
                ORDER BY count DESC
            """)
            
            category_counts = cursor.fetchall()
            print("\nItem counts by category:")
            for cat in category_counts:
                if cat[0]:  # Skip None categories
                    print(f"  {cat[0]}: {cat[1]}")
            
            # Check 'tops' specifically
            cursor.execute("SELECT COUNT(*) FROM wardrobe_items WHERE category = 'tops'")
            tops_count = cursor.fetchone()[0]
            print(f"\nItems with category 'tops': {tops_count}")
            
            # Get raw data for a few items
            cursor.execute("SELECT * FROM wardrobe_items LIMIT 2")
            sample_items = cursor.fetchall()
            
            print("\nSample items (raw data):")
            for item in sample_items:
                print(f"  Item type: {type(item)}")
                if hasattr(item, 'keys'):
                    print(f"  Keys: {list(item.keys())}")
                    print(f"  Item data: {dict(item)}")
                else:
                    print(f"  Item data: {item}")
            
    except Exception as e:
        print(f"Error checking categories: {e}")

if __name__ == "__main__":
    check_categories()
