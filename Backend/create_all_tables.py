"""
Complete database schema creation script for Styra AI Wardrobe App
This script creates all tables based on the SQLAlchemy models in all_models.py
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def create_all_tables():
    """Create all database tables with proper relationships"""
    try:
        # Database connection
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "123456")
            database = os.getenv("DB_NAME", "styra_wardrobe")
            DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
        
        with conn.cursor() as cursor:
            print("Creating Styra AI Wardrobe Database Schema...")
            
            # Drop all tables if they exist (in reverse dependency order)
            drop_tables = [
                "DROP TABLE IF EXISTS user_preferences CASCADE;",
                "DROP TABLE IF EXISTS image_processing_cache CASCADE;",
                "DROP TABLE IF EXISTS weather_cache CASCADE;",
                # buying_recommendations removed
                "DROP TABLE IF EXISTS analysis_history CASCADE;",
                "DROP TABLE IF EXISTS outfit_items CASCADE;",
                "DROP TABLE IF EXISTS favorite_outfits CASCADE;",
                "DROP TABLE IF EXISTS outfit_history CASCADE;",
                "DROP TABLE IF EXISTS wardrobe_items CASCADE;",
                "DROP TABLE IF EXISTS users CASCADE;",
                "DROP TYPE IF EXISTS packingstyle CASCADE;",
                "DROP TYPE IF EXISTS season CASCADE;",
                "DROP TYPE IF EXISTS occasion CASCADE;"
            ]
            
            print("Dropping existing tables and types...")
            for drop_sql in drop_tables:
                cursor.execute(drop_sql)
            
            # Create custom ENUM types
            print("Creating ENUM types...")
            
            cursor.execute("""
                CREATE TYPE packingstyle AS ENUM (
                    'minimal', 'comfort', 'fashion', 'business'
                );
            """)
            
            cursor.execute("""
                CREATE TYPE season AS ENUM (
                    'spring', 'summer', 'fall', 'winter', 'all'
                );
            """)
            
            cursor.execute("""
                CREATE TYPE occasion AS ENUM (
                    'casual', 'formal', 'business', 'athletic', 
                    'beachwear', 'party', 'datenight', 'seasonal'
                );
            """)
            
            # 1. Users table (no dependencies)
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) NOT NULL,
                    full_name VARCHAR(255),
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_users_email ON users(email);
            """)
            
            # 2. Wardrobe Items table (depends on users)
            print("Creating wardrobe_items table...")
            cursor.execute("""
                CREATE TABLE wardrobe_items (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    color VARCHAR(100),
                    brand VARCHAR(100),
                    season season DEFAULT 'all',
                    occasion occasion DEFAULT 'casual',
                    image_url VARCHAR(500),
                    image_path VARCHAR(500),
                    times_worn INTEGER DEFAULT 0,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    pending_sync BOOLEAN DEFAULT false,
                    ai_tags JSONB,
                    style_confidence DECIMAL(5,3),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Additional columns for compatibility with current service
                    confidence DECIMAL(5,3),
                    analysis_method VARCHAR(100),
                    last_worn TIMESTAMP
                );
                
                CREATE INDEX idx_wardrobe_items_user_id ON wardrobe_items(user_id);
                CREATE INDEX idx_wardrobe_items_category ON wardrobe_items(category);
            """)
            
            # 3. Outfit History table (depends on users)
            print("Creating outfit_history table...")
            cursor.execute("""
                CREATE TABLE outfit_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    worn_date TIMESTAMP NOT NULL,
                    occasion occasion,
                    weather VARCHAR(100),
                    location VARCHAR(255),
                    -- Optional image columns for quick thumbnails
                    image_url VARCHAR(500),
                    image_path VARCHAR(500),
                    confidence_score DECIMAL(5,3),
                    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                    notes TEXT,
                    outfit_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_outfit_history_user_id ON outfit_history(user_id);
                CREATE INDEX idx_outfit_history_worn_date ON outfit_history(worn_date);
            """)
            
            # 4. Favorite Outfits table (depends on users)
            print("Creating favorite_outfits table...")
            cursor.execute("""
                CREATE TABLE favorite_outfits (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    outfit_data JSONB,
                    -- Optional image columns for thumbnail display
                    image_url VARCHAR(500),
                    image_path VARCHAR(500),
                    occasion occasion,
                    confidence_score DECIMAL(5,3),
                    times_worn INTEGER DEFAULT 0,
                    notes TEXT,
                    weather_context JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_favorite_outfits_user_id ON favorite_outfits(user_id);
            """)
            
            # 5. Outfit Items table (junction table - depends on outfit_history, favorite_outfits, wardrobe_items)
            print("Creating outfit_items table...")
            cursor.execute("""
                CREATE TABLE outfit_items (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    outfit_history_id INTEGER REFERENCES outfit_history(id) ON DELETE CASCADE,
                    favorite_outfit_id INTEGER REFERENCES favorite_outfits(id) ON DELETE CASCADE,
                    wardrobe_item_id INTEGER NOT NULL REFERENCES wardrobe_items(id) ON DELETE CASCADE,
                    
                    CHECK (
                        (outfit_history_id IS NOT NULL AND favorite_outfit_id IS NULL) OR
                        (outfit_history_id IS NULL AND favorite_outfit_id IS NOT NULL)
                    )
                );
                -- IMPORTANT: Each outfit_items row must include the user_id of the owner.
                -- This enforces explicit ownership so users cannot see or manipulate others' outfits.
                
                CREATE INDEX idx_outfit_items_user_id ON outfit_items(user_id);
                CREATE INDEX idx_outfit_items_outfit_history ON outfit_items(outfit_history_id);
                CREATE INDEX idx_outfit_items_favorite_outfit ON outfit_items(favorite_outfit_id);
                CREATE INDEX idx_outfit_items_wardrobe_item ON outfit_items(wardrobe_item_id);
            """)
            
            
            # 7. Analysis History table (depends on users)
            print("Creating analysis_history table...")
            cursor.execute("""
                CREATE TABLE analysis_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    analysis_type VARCHAR(100) NOT NULL,
                    input_data JSONB,
                    result_data JSONB,
                    confidence_score DECIMAL(5,3),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_analysis_history_user_id ON analysis_history(user_id);
                CREATE INDEX idx_analysis_history_type ON analysis_history(analysis_type);
                CREATE INDEX idx_analysis_history_created ON analysis_history(created_at);
            """)
            
            # buying_recommendations table removed from schema by request
            
            # 9. Weather Cache table (no dependencies)
            print("Creating weather_cache table...")
            cursor.execute("""
                CREATE TABLE weather_cache (
                    id SERIAL PRIMARY KEY,
                    latitude DECIMAL(10,8) NOT NULL,
                    longitude DECIMAL(11,8) NOT NULL,
                    weather_data JSONB NOT NULL,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                );
                
                CREATE INDEX idx_weather_cache_location ON weather_cache(latitude, longitude);
                CREATE INDEX idx_weather_cache_expires ON weather_cache(expires_at);
            """)
            
            # 10. Image Processing Cache table (no dependencies)
            print("Creating image_processing_cache table...")
            cursor.execute("""
                CREATE TABLE image_processing_cache (
                    id SERIAL PRIMARY KEY,
                    image_hash VARCHAR(64) UNIQUE NOT NULL,
                    processing_result JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_image_processing_cache_hash ON image_processing_cache(image_hash);
            """)
            
            # 11. User Preferences table (depends on users)
            print("Creating user_preferences table...")
            cursor.execute("""
                CREATE TABLE user_preferences (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    preferred_colors JSONB,
                    preferred_styles JSONB,
                    body_type VARCHAR(50),
                    size_preferences JSONB,
                    budget_range JSONB,
                    style_personality VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
            """)
            
            # Create update triggers for updated_at columns
            print("Creating update triggers...")
            
            # Function to update updated_at timestamp
            cursor.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """)
            
            # Add triggers to tables with updated_at columns
            tables_with_updated_at = [
                'users', 'wardrobe_items', 'favorite_outfits', 
                'user_preferences'
            ]
            
            for table in tables_with_updated_at:
                cursor.execute(f"""
                    CREATE TRIGGER update_{table}_updated_at 
                    BEFORE UPDATE ON {table} 
                    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                """)
            
            conn.commit()
            print("All tables created successfully!")
            
            # Test the schema by inserting a test user and wardrobe item
            print("\nTesting schema with sample data...")
            
            # Insert test user
            test_user_sql = """
                INSERT INTO users (email, username, full_name, hashed_password, is_active)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, email
            """
            cursor.execute(test_user_sql, (
                'test@styra.ai', 'testuser', 'Test User', 
                '$2b$12$dummy.hash.for.testing', True
            ))
            
            test_user = cursor.fetchone()
            print(f"Test user created: {test_user['email']} (ID: {test_user['id']})")
            
            # Insert test wardrobe item
            test_item_sql = """
                INSERT INTO wardrobe_items 
                (user_id, name, category, color, season, confidence, analysis_method)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, name
            """
            cursor.execute(test_item_sql, (
                test_user['id'], 'Test Blue Shirt', 'tops', 'blue', 
                'summer', 0.95, 'ai_vision'
            ))
            
            test_item = cursor.fetchone()
            print(f"Test wardrobe item created: {test_item['name']} (ID: {test_item['id']})")
            
            # Clean up test data
            cursor.execute("DELETE FROM wardrobe_items WHERE id = %s", (test_item['id'],))
            cursor.execute("DELETE FROM users WHERE id = %s", (test_user['id'],))
            print("Test data cleaned up")
            
            conn.commit()
        
        conn.close()
        print("\nComplete database schema created successfully!")
        print("\nTables created:")
        print("- users")
        print("- wardrobe_items")
        print("- outfit_history")
        print("- favorite_outfits")
        print("- outfit_items")
        print("- analysis_history")
        print("- weather_cache")
        print("- image_processing_cache")
        print("- user_preferences")
        print("\nENUM types created:")
        print("- packingstyle")
        print("- season")
        print("- occasion")
        
    except Exception as e:
        print(f"Error creating database schema: {e}")
        import traceback
        traceback.print_exc()

def show_table_info():
    """Show information about all created tables"""
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
        
        with conn.cursor() as cursor:
            # Get all tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            
            print("\n Database Tables Information:")
            print("=" * 50)
            
            for table in tables:
                table_name = table['table_name']
                print(f"\n  Table: {table_name}")
                
                # Get column information
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position;
                """, (table_name,))
                
                columns = cursor.fetchall()
                
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"   • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error showing table info: {e}")

if __name__ == "__main__":
    print("Styra AI Wardrobe Database Setup")
    print("=" * 40)
    
    response = input("This will drop and recreate all tables. Continue? (y/N): ")
    if response.lower() in ['y', 'yes']:
        create_all_tables()
        
        show_info = input("\nShow detailed table information? (y/N): ")
        if show_info.lower() in ['y', 'yes']:
            show_table_info()
    else:
        print("Database setup cancelled.")