# Backend/test_env.py
import os
from dotenv import load_dotenv

print("Before loading .env:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

load_dotenv()

print("\nAfter loading .env:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"HOST: {os.getenv('HOST')}")
print(f"PORT: {os.getenv('PORT')}")

# Check if .env file exists
env_path = os.path.join(os.getcwd(), '.env')
print(f"\n.env file exists: {os.path.exists(env_path)}")
print(f"Current directory: {os.getcwd()}")