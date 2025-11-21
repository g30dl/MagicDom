"""
Paquete de entidades del juego.

Evitar importaciones ansiosas para no provocar ciclos durante la carga.
Importa submódulos directamente donde se necesiten:
  from src.entities.player import Player
  from src.entities.enemy import Enemy
  from src.entities.spell import Spell
"""

__all__ = [
    'player',
    'enemy',
    'spell',
]

