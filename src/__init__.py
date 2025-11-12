"""
Paquete raíz del proyecto `src`.

Este archivo expone los subpaquetes principales para importaciones de paquete
como `from src import game`.
"""

__all__ = [
	'game',
	'rendering',
	'entities',
	'input',
	'audio',
	'utils',
]

# No importamos aquí los submódulos directamente para evitar efectos secundarios
# en la importación (cargar pygame u otros subsistemas). Los módulos pueden
# seguir importándose con `from src.rendering import renderer` o
# `from src import game`.
