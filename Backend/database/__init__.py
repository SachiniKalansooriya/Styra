# Database package initialization
# Backend/database/__init__.py
from .connection import db, DatabaseConnection

__all__ = ['db', 'DatabaseConnection']