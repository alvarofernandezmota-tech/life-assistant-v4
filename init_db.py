#!/usr/bin/env python3
"""
init_db.py - Inicializa la base de datos con tablas y seed data
Actualizado 2026-03-08: corregidos imports para funcionar desde raíz

Uso:
    python init_db.py
"""
import sys
from pathlib import Path

# Añadir raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.database import Base, engine, SessionLocal
from src.core.models import *
from src.core.rpg_models import *


def create_tables():
    print("🛠️  Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas correctamente")


def seed_artifacts():
    db = SessionLocal()

    if db.query(Artifact).count() > 0:
        print("ℹ️  Artefactos ya existen, saltando seed...")
        db.close()
        return

    print("🎮 Insertando artefactos míticos...")

    artifacts = [
        # ── COMMON (comprables en mercado + drops de Póker) ──────────
        Artifact(
            id="sandalias_hermes", name="Sandalias de Hermes", hero_origin="Hermes",
            emoji="👟", rarity="common",
            description="Alas en los pies del mensajero.",
            effect="+1 dado en la próxima tirada", effect_type="bonus_die", effect_value=1,
            price_type="tetradracma", price=6,
        ),
        Artifact(
            id="egida_atenea", name="Égida de Atenea", hero_origin="Atenea",
            emoji="🛡️", rarity="common",
            description="Escudo divino de la diosa sabiduría.",
            effect="El siguiente mal hábito no quita Wyrd", effect_type="shield_bad_habit", effect_value=1,
            price_type="tetradracma", price=8,
        ),
        Artifact(
            id="laurel_apolo", name="Corona de Laurel", hero_origin="Apolo",
            emoji="🌿", rarity="common",
            description="Símbolo de victoria y sabiduría.",
            effect="+20% XP durante 3 días", effect_type="xp_boost", effect_value=3,
            price_type="tetradracma", price=7,
        ),
        Artifact(
            id="arco_apolo", name="Arco de Apolo", hero_origin="Apolo",
            emoji="🏹", rarity="common",
            description="Precisión divina del dios del sol.",
            effect="Hábito a medias cuenta como completo x1", effect_type="half_habit_ok", effect_value=1,
            price_type="tetradracma", price=7,
        ),
        # ── RARE (drops de Triple Ánfora) ──────────────────
        Artifact(
            id="lira_orfeo", name="Lira de Orfeo", hero_origin="Orfeo",
            emoji="🎵", rarity="rare",
            description="Encantó a Caronte con su música.",
            effect="Recupera 15 Wyrd una vez por semana", effect_type="heal_wyrd_weekly", effect_value=15,
            price_type="tetradracma", price=5,
        ),
        Artifact(
            id="casco_hades", name="Casco de Hades", hero_origin="Hades",
            emoji="⛑️", rarity="rare",
            description="El casco que hace invisible al portador.",
            effect="Inmortalidad 24h — un mal hábito no aplica", effect_type="immunity_24h", effect_value=1,
            price_type="tetradracma", price=15,
        ),
        Artifact(
            id="tridente_poseidon", name="Tridente de Poseidón", hero_origin="Poseidón",
            emoji="🔱", rarity="rare",
            description="Control absoluto sobre las aguas.",
            effect="+3 dados durante 2 días", effect_type="bonus_dice_days", effect_value=2,
            price_type="tetradracma", price=9,
        ),
        Artifact(
            id="hilo_ariadna", name="Hilo de Ariadna", hero_origin="Ariadna",
            emoji="🧶", rarity="rare",
            description="El hilo que guió a Teseo en el laberinto.",
            effect="Recupera racha rota 1 vez", effect_type="recover_streak", effect_value=1,
            price_type="tetradracma", price=20,
        ),
        # ── LEGENDARY (drops de Repóker) ─────────────────
        Artifact(
            id="rayo_zeus", name="Rayo de Zeus", hero_origin="Zeus",
            emoji="⚡", rarity="legendary",
            description="El arma definitiva del rey de los dioses.",
            effect="Dobla todas las recompensas del día siguiente", effect_type="double_rewards", effect_value=1,
            price_type="tetradracma", price=12,
        ),
        Artifact(
            id="caduceo_hermes", name="Caduceo de Hermes", hero_origin="Hermes",
            emoji="🐍", rarity="legendary",
            description="El bastón que cura y guía almas.",
            effect="Cura +20 Wyrd inmediatamente", effect_type="heal_wyrd", effect_value=20,
            price_type="tetradracma", price=10,
        ),
        Artifact(
            id="armadura_aquiles", name="Armadura de Aquiles", hero_origin="Aquiles",
            emoji="⚔️", rarity="legendary",
            description="Forjada por Hefesto. Casi invulnerable.",
            effect="Reduce daño malos hábitos al 50% durante 3 días", effect_type="damage_reduction", effect_value=3,
            price_type="tetradracma", price=25,
        ),
        Artifact(
            id="moneda_caronte", name="Moneda de Caronte", hero_origin="Caronte",
            emoji="🌑", rarity="legendary",
            description="La moneda que abre la puerta del inframundo.",
            effect="5 indulgencias permanentes + inmunidad a Game Over una vez",
            effect_type="mega_indulgencia", effect_value=5,
            price_type="tetradracma", price=50,
        ),
    ]

    for a in artifacts:
        db.add(a)

    db.commit()
    print(f"✅ {len(artifacts)} artefactos insertados "
          f"({sum(1 for a in artifacts if a.rarity=='common')} common / "
          f"{sum(1 for a in artifacts if a.rarity=='rare')} rare / "
          f"{sum(1 for a in artifacts if a.rarity=='legendary')} legendary)")
    db.close()


def main():
    print("=" * 60)
    print("🚀 Life Assistant V4 — Inicialización de Base de Datos")
    print("=" * 60)
    create_tables()
    seed_artifacts()
    print("\n✅ Base de datos inicializada correctamente")
    print("🌊 Ya puedes iniciar la aplicación!")
    print("=" * 60)


if __name__ == "__main__":
    main()
