# Backend/database/connection.py
import psycopg2
import psycopg2.extras
import os
from contextlib import contextmanager
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        if not self.connection_string:
            # Try to construct from individual components
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "123456")
            database = os.getenv("DB_NAME", "styra_wardrobe")
            
            self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            print(f"Constructed DATABASE_URL: {self.connection_string}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                if cursor.description:
                    return cursor.fetchall()
                return None
            else:
                conn.commit()
                return cursor.rowcount
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                return {"status": "connected", "version": version[0]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

# Global database instance
db = DatabaseConnection()