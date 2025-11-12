"""
Funciones de carga de recursos sencillas (imagen/audio).
"""
import os
import pygame

def load_image(name: str):
	path = os.path.join('assets', 'textures', name)
	# intentar con extensiones comunes
	if not os.path.exists(path):
		for ext in ('.png', '.jpg', '.bmp'):
			alt = path + ext
			if os.path.exists(alt):
				path = alt
				break

	try:
		return pygame.image.load(path).convert_alpha()
	except Exception:
		# Devolver una Surface placeholder
		surf = pygame.Surface((32, 32))
		surf.fill((255, 0, 255))
		return surf
