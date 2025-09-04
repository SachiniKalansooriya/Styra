import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database.database import engine, Base
    from app.models.user import User
    from app.models.wardrobe_item import WardrobeItem
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all __init__.py files exist in app/, app/database/, and app/models/ directories")
    sys.exit(1)

def create_tables():
    try:
        print("Connecting to Supabase database...")
        
        print("Creating database tables...")
        
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        
        print("Tables created successfully!")
        print("\nCreated tables:")
        print("- users")
        print("- wardrobe_items")
        
        # Test the connection
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"Connected to database: {db_name}")
        
        print("\nDatabase setup complete! You can now run your backend.")
        
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        print("Make sure your .env file has the correct DATABASE_URL")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()