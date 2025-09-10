"""
Create and verify all database tables for the Styra application at once
"""
import logging
from database.connection import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_tables():
    """Create all required tables for the Styra application if they don't exist"""
    try:
        # Create all tables with one transaction
        create_tables_query = """
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Wardrobe items table
        CREATE TABLE IF NOT EXISTS wardrobe_items (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            color VARCHAR(50),
            season VARCHAR(20) DEFAULT 'all',
            image_path VARCHAR(500),
            confidence DECIMAL(5,2),
            analysis_method VARCHAR(50),
            times_worn INTEGER DEFAULT 0,
            last_worn DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Analysis history table
        CREATE TABLE IF NOT EXISTS analysis_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            image_path TEXT,
            analysis_result TEXT,
            confidence NUMERIC(5,2),
            category VARCHAR(100),
            color VARCHAR(50),
            pattern VARCHAR(100),
            detected_attributes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Outfit history table
        CREATE TABLE IF NOT EXISTS outfit_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            outfit_data TEXT NOT NULL,
            worn_date DATE NOT NULL,
            occasion VARCHAR(100),
            weather_condition VARCHAR(100),
            location VARCHAR(255),
            rating INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Favorite outfits table
        CREATE TABLE IF NOT EXISTS favorite_outfits (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            outfit_name VARCHAR(255) NOT NULL,
            outfit_data TEXT NOT NULL,
            occasion VARCHAR(100),
            season VARCHAR(50),
            weather_context TEXT,
            confidence_score INTEGER DEFAULT 0,
            notes TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            times_worn INTEGER DEFAULT 0,
            last_worn TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Trip plans table
        CREATE TABLE IF NOT EXISTS trip_plans (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            trip_name VARCHAR(255) NOT NULL,
            destination VARCHAR(255),
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            weather_forecast TEXT,
            activities TEXT,
            packing_list TEXT,
            is_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_wardrobe_items_user_id ON wardrobe_items(user_id);
        CREATE INDEX IF NOT EXISTS idx_wardrobe_items_category ON wardrobe_items(category);
        CREATE INDEX IF NOT EXISTS idx_outfit_history_user_id ON outfit_history(user_id);
        CREATE INDEX IF NOT EXISTS idx_favorite_outfits_user_id ON favorite_outfits(user_id);
        CREATE INDEX IF NOT EXISTS idx_trip_plans_user_id ON trip_plans(user_id);
        """
        
        db.execute_query(create_tables_query, fetch=False)
        logger.info("All tables created/verified successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False

def check_all_tables():
    """Check all tables existence and print their structure"""
    try:
        # Get all tables in the public schema
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
        tables = db.execute_query(query)
        
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            table_name = table['table_name']
            print(f"\n--- {table_name} ---")
            
            # Get table structure
            structure_query = f"""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """
            columns = db.execute_query(structure_query)
            
            for column in columns:
                max_length = column['character_maximum_length']
                max_length_str = f", Max Length: {max_length}" if max_length else ""
                print(f"  {column['column_name']} ({column['data_type']}{max_length_str})")
            
            # Count rows in table
            count_query = f"SELECT COUNT(*) as row_count FROM {table_name};"
            count_result = db.execute_query(count_query)
            row_count = count_result[0]['row_count'] if count_result else 0
            print(f"  Total rows: {row_count}")
            
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Setting up all database tables for Styra application...")
    
    if create_all_tables():
        print("\nAll tables created successfully!")
        print("\nChecking database structure...")
        check_all_tables()
    else:
        print("\nFailed to create all tables. Check the logs for errors.")
