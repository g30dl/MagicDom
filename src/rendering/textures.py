"""
Funciones simples para cargar texturas.
Si pygame no encuentra el archivo, se devuelve una Surface de placeholder.
"""
import os
import pygame
from src.game.config import Config

def load_texture(name: str):
	"""Intenta cargar una textura desde `assets/textures/{name}`.
	Retorna una `pygame.Surface`.
	"""
	assets_dir = os.path.join('assets', 'textures')
	filepath = os.path.join(assets_dir, name)
	if not os.path.exists(filepath):
		# Intentar con extensiones comunes
		for ext in ('.png', '.jpg', '.bmp'):
			alt = filepath + ext
			if os.path.exists(alt):
				filepath = alt
				break

	try:
		return pygame.image.load(filepath).convert_alpha()
	except Exception:
		# Placeholder simple
		surf = pygame.Surface((Config.TILE_SIZE, Config.TILE_SIZE))
		surf.fill((255, 0, 255))  # magenta para indicar textura faltante
		return surf
