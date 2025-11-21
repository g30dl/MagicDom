"""
Renderizado sencillo de hechizos (minimapa y overlay básico).
"""
import pygame
from src.game.config import Config


class SpellRenderer:
    def render_on_minimap(self, surface: pygame.Surface, spells, scale: int):
        if not spells:
            return
        for s in spells:
            x = int((s.x // Config.TILE_SIZE) * scale)
            y = int((s.y // Config.TILE_SIZE) * scale)
            color = getattr(s, 'color', (255, 255, 0))
            pygame.draw.circle(surface, color, (x, y), 3)

