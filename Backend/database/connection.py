import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseConnection:
    def __init__(self):
        self.connection_params = self._get_connection_params()
        self._test_connection()
    
    def _get_connection_params(self):
        """Get database connection parameters"""
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            return DATABASE_URL
        else:
            return {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": os.getenv("DB_PORT", "5432"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "123456"),
                "database": os.getenv("DB_NAME", "styra_wardrobe")
            }
    
    def _test_connection(self):
        """Test database connection on startup"""
        try:
            conn = self._create_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            conn.close()
            logger.info("Database connection test successful")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    def _create_connection(self):
        """Create a new database connection"""
        try:
            if isinstance(self.connection_params, str):
                conn = psycopg2.connect(
                    self.connection_params,
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
            else:
                conn = psycopg2.connect(
                    cursor_factory=psycopg2.extras.RealDictCursor,
                    **self.connection_params
                )
            return conn
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            raise
    
    def execute_query(self, query, params=None):
        """Execute query with proper connection handling"""
        conn = None
        try:
            conn = self._create_connection()
            with conn.cursor() as cursor:
                logger.debug(f"Executing: {query}")
                logger.debug(f"Params: {params}")
                
                cursor.execute(query, params)
                
                # Handle different query types
                if query.strip().upper().startswith('SELECT') or 'RETURNING' in query.upper():
                    if 'RETURNING' in query.upper():
                        result = cursor.fetchone()  # RETURNING typically returns one row
                    else:
                        result = cursor.fetchall()
                    
                    conn.commit()  # Commit even for SELECT with RETURNING
                    logger.debug(f"Query result: {result}")
                    return result
                else:
                    # INSERT/UPDATE/DELETE without RETURNING
                    affected_rows = cursor.rowcount
                    conn.commit()
                    logger.debug(f"Affected rows: {affected_rows}")
                    return affected_rows > 0
                    
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database query failed: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
        finally:
            if conn:
                conn.close()

# Global instance
db = DatabaseConnection()