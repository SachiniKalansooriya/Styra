# Backend/setup_database.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reset_database():
    """Drop and recreate the database"""
    try:
        # Connect to default postgres database first
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="123456",
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Terminate existing connections to the database
        cursor.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'styra_wardrobe' AND pid <> pg_backend_pid()
        """)
        
        # Drop database if exists
        cursor.execute("DROP DATABASE IF EXISTS styra_wardrobe")
        print("Dropped existing database 'styra_wardrobe'")
        
        # Create fresh database
        cursor.execute('CREATE DATABASE styra_wardrobe')
        print("Created fresh database 'styra_wardrobe'")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        return False
    
    return True

def setup_database():
    """Initialize the local database with schema and sample data"""
    try:
        # Reset the database first
        if not reset_database():
            return
        
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'init.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"Error: SQL file not found at {sql_file_path}")
            return
        
        with open(sql_file_path, 'r') as file:
            sql_commands = file.read()
        
        # Connect to the styra_wardrobe database
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("Error: DATABASE_URL not found in environment variables")
            return
            
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Execute the SQL commands
        cursor.execute(sql_commands)
        conn.commit()
        
        print("Database setup completed successfully!")
        
        # Verify setup
        cursor.execute("SELECT count(*) FROM users;")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT count(*) FROM wardrobe_items;")
        item_count = cursor.fetchone()[0]
        
        print(f"Database initialized with {user_count} users and {item_count} wardrobe items")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database setup failed: {e}")

if __name__ == "__main__":
    setup_database()