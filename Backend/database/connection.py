# Backend/database/connection.py
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            DATABASE_URL = os.getenv("DATABASE_URL")
            if not DATABASE_URL:
                host = os.getenv("DB_HOST", "localhost")
                port = os.getenv("DB_PORT", "5432")
                user = os.getenv("DB_USER", "postgres")
                password = os.getenv("DB_PASSWORD", "123456")
                database = os.getenv("DB_NAME", "styra_wardrobe")
                DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            
            self.connection = psycopg2.connect(
                DATABASE_URL,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            self.connection.autocommit = True
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.connection = None
    
    def get_connection(self):
        """Get database connection"""
        if not self.connection or self.connection.closed:
            self.connect()
        return self.connection
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            conn = self.get_connection()
            if not conn:
                raise Exception("No database connection")
            
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                elif 'RETURNING' in query.upper():
                    return cursor.fetchone()
                else:
                    return True
                    
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise e

# Global database instance
db = DatabaseConnection()