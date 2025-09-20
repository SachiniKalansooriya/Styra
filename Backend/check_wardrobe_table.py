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
    
    print("=== Checking wardrobe_items table ===")
    
    with conn.cursor() as cursor:
        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'wardrobe_items'
            );
        """)
        table_exists = cursor.fetchone()[0]
        print(f"Table exists: {table_exists}")
        
        if table_exists:
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'wardrobe_items'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
            
            # Try to get a few rows
            cursor.execute("SELECT * FROM wardrobe_items LIMIT 3;")
            rows = cursor.fetchall()
            print(f"\nSample data ({len(rows)} rows):")
            for row in rows:
                print(f"  {dict(row)}")
        else:
            print("Table does not exist!")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")