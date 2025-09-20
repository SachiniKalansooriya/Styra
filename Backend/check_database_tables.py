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
    
    print(f"Connecting to: {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    
    print("=== Database Tables ===")
    
    with conn.cursor() as cursor:
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
    
    conn.close()
    print("\nConnection successful!")
    
except Exception as e:
    print(f"Database connection error: {e}")
    import traceback
    traceback.print_exc()