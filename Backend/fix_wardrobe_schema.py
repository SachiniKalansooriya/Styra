import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

try:
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "123456")
        database = os.getenv("DB_NAME", "styra_wardrobe")
        DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("=== Checking and Fixing wardrobe_items table ===")
    
    with conn.cursor() as cursor:
        # Get current table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'wardrobe_items'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        existing_columns = [col['column_name'] for col in columns]
        
        print("Current columns:")
        for col in columns:
            print(f"  {col['column_name']}: {col['data_type']}")
        
        # Add missing columns
        missing_columns = []
        
        if 'analysis_method' not in existing_columns:
            print("\nAdding analysis_method column...")
            cursor.execute("ALTER TABLE wardrobe_items ADD COLUMN analysis_method VARCHAR(100);")
            missing_columns.append('analysis_method')
        
        if 'times_worn' not in existing_columns:
            print("Adding times_worn column...")
            cursor.execute("ALTER TABLE wardrobe_items ADD COLUMN times_worn INTEGER DEFAULT 0;")
            missing_columns.append('times_worn')
        
        if 'last_worn' not in existing_columns:
            print("Adding last_worn column...")
            cursor.execute("ALTER TABLE wardrobe_items ADD COLUMN last_worn TIMESTAMP;")
            missing_columns.append('last_worn')
        
        if 'confidence' not in existing_columns:
            print("Adding confidence column...")
            cursor.execute("ALTER TABLE wardrobe_items ADD COLUMN confidence DECIMAL(5,3);")
            missing_columns.append('confidence')
        
        if missing_columns:
            conn.commit()
            print(f"\nAdded missing columns: {missing_columns}")
        else:
            print("\nAll required columns already exist!")
        
        # Verify the final structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'wardrobe_items'
            ORDER BY ordinal_position;
        """)
        final_columns = cursor.fetchall()
        print("\nFinal table structure:")
        for col in final_columns:
            print(f"  {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
    
    conn.close()
    print("\n✅ Database schema update completed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()