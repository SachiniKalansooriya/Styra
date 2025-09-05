# Backend/test_complete_system.py
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

import requests
from database.connection import db
from image_analysis import image_analysis_service

def test_database():
    """Test database connection"""
    print("Testing database connection...")
    try:
        # Check if DATABASE_URL is loaded
        db_url = os.getenv("DATABASE_URL")
        print(f"DATABASE_URL: {db_url[:30]}..." if db_url else "DATABASE_URL not found")
        
        result = db.test_connection()
        print(f"Database: {result}")
        
        # Test data
        users = db.execute_query("SELECT * FROM users")
        items = db.execute_query("SELECT * FROM wardrobe_items")
        print(f"Found {len(users)} users and {len(items)} wardrobe items")
        
        return True
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def test_ai_service():
    """Test AI service"""
    print("Testing AI service...")
    try:
        status = image_analysis_service.get_service_info()
        print(f"AI Service Status: {status}")
        return True
    except Exception as e:
        print(f"AI service test failed: {e}")
        return False

def test_server():
    """Test if server is running"""
    print("Testing server...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"Server health: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Server test failed: {e}")
        return False

def main():
    print("=== Complete System Test ===\n")
    
    # Check environment variables first
    print("Environment variables:")
    print(f"DATABASE_URL: {'SET' if os.getenv('DATABASE_URL') else 'NOT SET'}")
    print(f"HOST: {os.getenv('HOST', 'default')}")
    print(f"PORT: {os.getenv('PORT', 'default')}")
    print("")
    
    db_ok = test_database()
    ai_ok = test_ai_service()
    
    print(f"\n=== Test Results ===")
    print(f"Database: {'PASS' if db_ok else 'FAIL'}")
    print(f"AI Service: {'PASS' if ai_ok else 'FAIL'}")
    
    if db_ok and ai_ok:
        print("\nSystem ready! You can now start the server.")
        print("Run: python run.py")
    else:
        print("\nSome components failed. Check the errors above.")

if __name__ == "__main__":
    main()