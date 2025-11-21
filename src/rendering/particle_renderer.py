"""
Renderizado sencillo de partículas (minimapa).
"""
import pygame
from src.game.config import Config


class ParticleRenderer:
    def render_on_minimap(self, surface: pygame.Surface, particles, scale: int):
        if not particles:
            return
        for p in particles:
            x = int((p.x // Config.TILE_SIZE) * scale)
            y = int((p.y // Config.TILE_SIZE) * scale)
            color = getattr(p, 'color', (255, 255, 255))
            size = max(1, int(getattr(p, 'size', 2)))
            pygame.draw.circle(surface, color, (x, y), size)

