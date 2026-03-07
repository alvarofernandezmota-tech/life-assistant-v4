#!/usr/bin/env python3
"""
init_db.py - Inicializa la base de datos con tablas y seed data

Uso:
    python init_db.py
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.database import Base, engine, SessionLocal
from core.rpg_models import Artifact
from core.models import *
from core.rpg_models import *

def create_tables():
    """Crea todas las tablas en la base de datos"""
    print("🛠️  Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")

def seed_artifacts():
    """Inserta el catálogo de artefactos míticos"""
    db = SessionLocal()
    
    if db.query(Artifact).count() > 0:
        print("ℹ️  Artefactos ya existen, saltando seed...")
        db.close()
        return
    
    print("🎮 Insertando artefactos míticos...")
    
    artifacts = [
        Artifact(
            id="lira_orfeo",
            name="Lira de Orfeo",
            hero_origin="Orfeo",
            emoji="🎵",
            description="Encantó a Caronte con su música.",
            effect="Reduce penalización x1",
            effect_type="reduce_penalty",
            effect_value=1,
            price_type="tetradracma",
            price=5
        ),
        Artifact(
            id="egida_atenea",
            name="Égida de Atenea",
            hero_origin="Atenea",
            emoji="🛡️",
            description="Escudo divino de la diosa sabiduría.",
            effect="Protege racha 1 vez",
            effect_type="shield_streak",
            effect_value=1,
            price_type="tetradracma",
            price=8
        ),
        Artifact(
            id="sandalias_hermes",
            name="Sandalias de Hermes",
            hero_origin="Hermes",
            emoji="👟",
            description="Alas en los pies del mensajero.",
            effect="Recordatorios prioritarios activos",
            effect_type="priority_reminders",
            effect_value=7,
            price_type="tetradracma",
            price=6
        ),
        Artifact(
            id="casco_hades",
            name="Casco de Hades",
            hero_origin="Hades",
            emoji="🪖",
            description="El casco que hace invisible al portador.",
            effect="Salta 1 día sin penalización",
            effect_type="skip_day",
            effect_value=1,
            price_type="tetradracma",
            price=15
        ),
        Artifact(
            id="rayo_zeus",
            name="Rayo de Zeus",
            hero_origin="Zeus",
            emoji="⚡",
            description="El arma definitiva del rey de los dioses.",
            effect="Dobla XP durante 24h",
            effect_type="double_xp",
            effect_value=1,
            price_type="tetradracma",
            price=12
        ),
        Artifact(
            id="arco_apolo",
            name="Arco de Apolo",
            hero_origin="Apolo",
            emoji="🏹",
            description="Precisión divina del dios del sol.",
            effect="Hábito a medias cuenta como completo x1",
            effect_type="half_habit_ok",
            effect_value=1,
            price_type="tetradracma",
            price=7
        ),
        Artifact(
            id="caduceo_hermes",
            name="Caduceo de Hermes",
            hero_origin="Hermes",
            emoji="🐍",
            description="El bastón que cura y guía almas.",
            effect="Cura +20 Wyrd inmediatamente",
            effect_type="heal_wyrd",
            effect_value=20,
            price_type="tetradracma",
            price=10
        ),
        Artifact(
            id="hilo_ariadna",
            name="Hilo de Ariadna",
            hero_origin="Ariadna",
            emoji="🧶",
            description="El hilo que guió a Teseo en el laberinto.",
            effect="Recupera racha rota 1 vez",
            effect_type="recover_streak",
            effect_value=1,
            price_type="tetradracma",
            price=20
        ),
        Artifact(
            id="tridente_poseidon",
            name="Tridente de Poseidón",
            hero_origin="Poseidón",
            emoji="🔱",
            description="Control absoluto sobre las aguas.",
            effect="Mueve tarea vencida sin penalización",
            effect_type="move_task",
            effect_value=1,
            price_type="tetradracma",
            price=9
        ),
        Artifact(
            id="armadura_aquiles",
            name="Armadura de Aquiles",
            hero_origin="Aquiles",
            emoji="⚔️",
            description="Forjada por Hefesto. Casi invulnerable.",
            effect="Reduce daño malos hábitos al 50% por 3 días",
            effect_type="damage_reduction",
            effect_value=3,
            price_type="tetradracma",
            price=25
        ),
    ]
    
    for artifact in artifacts:
        db.add(artifact)
    
    db.commit()
    print(f"✅ {len(artifacts)} artefactos insertados")
    db.close()

def main():
    """Función principal"""
    print("="*60)
    print("🚀 Life Assistant V4 - Inicialización de Base de Datos")
    print("="*60)
    
    create_tables()
    seed_artifacts()
    
    print("\n✅ Base de datos inicializada correctamente")
    print("🌊 Ya puedes iniciar la aplicación!")
    print("="*60)

if __name__ == "__main__":
    main()