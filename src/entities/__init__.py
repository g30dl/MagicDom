"""
Paquete de entidades del juego.

Exporta los módulos que contienen las entidades (player, enemy, spell).
Importamos módulos para no forzar la carga de clases que todavía puedan
estar vacías.
"""

from . import player
from . import enemy
from . import spell

__all__ = [
	'player',
	'enemy',
	'spell',
]
