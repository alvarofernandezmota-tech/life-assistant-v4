"""
test_database.py - Tests básicos de conexión a base de datos
"""
import pytest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.database import SessionLocal, Base, engine, get_db
from core.models import Habit, Task, Event
from core.rpg_models import UserProfile, Artifact

class TestDatabase:
    """Tests de conexión y modelos de base de datos"""
    
    def test_connection(self):
        """Test de conexión básica a la base de datos"""
        db = SessionLocal()
        assert db is not None
        db.close()
    
    def test_create_habit(self):
        """Test de creación de hábito"""
        db = SessionLocal()
        
        habit = Habit(
            name="Test Habit",
            description="Habit de prueba",
            frequency="daily"
        )
        
        db.add(habit)
        db.commit()
        
        # Verificar que se creó
        retrieved = db.query(Habit).filter(Habit.name == "Test Habit").first()
        assert retrieved is not None
        assert retrieved.name == "Test Habit"
        
        # Limpiar
        db.delete(retrieved)
        db.commit()
        db.close()
    
    def test_create_task(self):
        """Test de creación de tarea"""
        db = SessionLocal()
        
        task = Task(
            title="Test Task",
            description="Tarea de prueba",
            priority="high"
        )
        
        db.add(task)
        db.commit()
        
        retrieved = db.query(Task).filter(Task.title == "Test Task").first()
        assert retrieved is not None
        assert retrieved.priority == "high"
        
        db.delete(retrieved)
        db.commit()
        db.close()
    
    def test_user_profile(self):
        """Test de creación de perfil RPG"""
        db = SessionLocal()
        
        # Verificar si ya existe
        existing = db.query(UserProfile).filter(UserProfile.user_id == 999).first()
        if existing:
            db.delete(existing)
            db.commit()
        
        profile = UserProfile(
            user_id=999,
            level=1,
            xp=0,
            wyrd=100
        )
        
        db.add(profile)
        db.commit()
        
        retrieved = db.query(UserProfile).filter(UserProfile.user_id == 999).first()
        assert retrieved is not None
        assert retrieved.wyrd == 100
        
        db.delete(retrieved)
        db.commit()
        db.close()
    
    def test_get_db_dependency(self):
        """Test del dependency get_db para FastAPI"""
        db_gen = get_db()
        db = next(db_gen)
        
        assert db is not None
        
        # Cerrar generador
        try:
            next(db_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])