# Backend/setup_fresh_database.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    """Set up database with all required tables"""
    try:
        # Connect to database
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", "5432")
            user = os.getenv("DB_USER", "postgres")
            password = os.getenv("DB_PASSWORD", "123456")
            database = os.getenv("DB_NAME", "styra_wardrobe")
            DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Creating database tables...")
        
        # Drop existing tables if they exist (fresh start)
        cursor.execute("""
            DROP TABLE IF EXISTS analysis_history CASCADE;
            DROP TABLE IF EXISTS favorite_outfits CASCADE;
            DROP TABLE IF EXISTS outfit_history CASCADE;
            DROP TABLE IF EXISTS trips CASCADE;
            DROP TABLE IF EXISTS wardrobe_items CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """)
        print("Dropped existing tables")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Created users table")
        
        # Create wardrobe_items table with ALL columns your app needs
        cursor.execute("""
            CREATE TABLE wardrobe_items (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL DEFAULT 1,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                color VARCHAR(100),
                brand VARCHAR(100),
                season VARCHAR(50) DEFAULT 'all',
                occasion VARCHAR(100) DEFAULT 'casual',
                image_url VARCHAR(500),
                image_path VARCHAR(500),
                times_worn INTEGER DEFAULT 0,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pending_sync BOOLEAN DEFAULT FALSE,
                confidence DECIMAL(5,2) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Created wardrobe_items table")
        
        # Create trips table
        cursor.execute("""
            CREATE TABLE trips (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL DEFAULT 1,
                destination VARCHAR(255) NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                activities JSONB,
                weather_expected VARCHAR(100),
                packing_style VARCHAR(50) DEFAULT 'minimal',
                packing_list JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Created trips table")
        
        # Create outfit_history table
        cursor.execute("""
            CREATE TABLE outfit_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL DEFAULT 1,
                worn_date DATE NOT NULL,
                occasion VARCHAR(100),
                weather VARCHAR(100),
                location VARCHAR(255),
                confidence_score DECIMAL(5,2),
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                notes TEXT,
                outfit_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Created outfit_history table")
        
        # Create favorite_outfits table
        cursor.execute("""
            CREATE TABLE favorite_outfits (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL DEFAULT 1,
                name VARCHAR(255) NOT NULL,
                outfit_data JSONB NOT NULL,
                occasion VARCHAR(100),
                confidence_score DECIMAL(5,2),
                times_worn INTEGER DEFAULT 0,
                notes TEXT,
                weather_context JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Created favorite_outfits table")
        
        # Create analysis_history table
        cursor.execute("""
            CREATE TABLE analysis_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER DEFAULT 1,
                analysis_type VARCHAR(100),
                input_data JSONB,
                result_data JSONB,
                confidence_score DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)
        print("Created analysis_history table")
        
        # Insert default user
        cursor.execute("""
            INSERT INTO users (id, email, username, hashed_password, full_name, is_active)
            VALUES (1, 'demo@styra.com', 'Demo User', '$2b$12$dummy.hash.for.demo', 'Demo User', TRUE);
        """)
        print("Created default user")
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX idx_wardrobe_items_user_id ON wardrobe_items(user_id);
            CREATE INDEX idx_wardrobe_items_category ON wardrobe_items(category);
            CREATE INDEX idx_outfit_history_user_id ON outfit_history(user_id);
            CREATE INDEX idx_favorite_outfits_user_id ON favorite_outfits(user_id);
            CREATE INDEX idx_trips_user_id ON trips(user_id);
        """)
        print("Created indexes")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database setup completed successfully!")
        print("✅ All tables created with proper columns")
        print("✅ Foreign keys and indexes added")
        print("✅ Default user created (ID: 1)")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == "__main__":
    setup_database()