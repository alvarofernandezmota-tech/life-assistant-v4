"""
database.py - Configuración de conexión a base de datos SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import sqlite3
from ..config.settings import settings

# SQLAlchemy setup
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Solo para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency para FastAPI - Sesión SQLAlchemy"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_connection():
    """Conexión directa SQLite - Para operaciones rápidas"""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializar base de datos - Crear todas las tablas"""
    from . import models  # Import here to avoid circular imports
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos inicializada correctamente")