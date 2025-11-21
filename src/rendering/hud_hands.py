"""
HUD de manos: dibuja sprites de manos en primera persona.
Busca archivos en assets/sprites:
  - hands_idle.png (pose normal)
  - hands_cast.png (pose de casteo)
Si no existen, usa placeholders.
"""
import os
import pygame
from src.game.config import Config


class HUDHands:
    def __init__(self):
        self.sprites_dir = os.path.join('assets', 'sprites')
        self.idle = self._load_sprite('hands_idle.png', fallback_color=(200, 200, 200))
        self.cast = self._load_sprite('hands_cast.png', fallback_color=(255, 200, 120))
        self.current = self.idle

        # Animación simple de casteo
        self.cast_time_total = 0.2
        self.cast_time_left = 0.0

        # Bobbing suave
        self.time = 0.0

    def _load_sprite(self, filename, fallback_color=(255, 0, 255)):
        path = os.path.join(self.sprites_dir, filename)
        try:
            if os.path.exists(path):
                return pygame.image.load(path).convert_alpha()
        except Exception:
            pass
        # Placeholder
        surf = pygame.Surface((256, 256), pygame.SRCALPHA)
        surf.fill((*fallback_color, 220))
        return surf

    def trigger_cast(self):
        self.cast_time_left = self.cast_time_total

    def update(self, dt: float):
        self.time += dt
        if self.cast_time_left > 0:
            self.cast_time_left -= dt
            self.current = self.cast
        else:
            self.current = self.idle

    def draw(self, screen: pygame.Surface):
        if not self.current:
            return
        sw, sh = screen.get_width(), screen.get_height()

        # Escala adaptable a pantalla: prioriza alto, limita ancho
        ratio = self.current.get_width() / max(1, self.current.get_height())
        target_h = int(sh * getattr(Config, 'HUD_HANDS_HEIGHT_RATIO', 0.6))
        target_w = int(target_h * ratio)
        max_w = int(sw * getattr(Config, 'HUD_HANDS_MAX_WIDTH_RATIO', 0.95))
        if target_w > max_w:
            target_w = max_w
            target_h = int(target_w / max(ratio, 0.0001))
        sprite = pygame.transform.smoothscale(self.current, (target_w, target_h))

        # Bobbing
        import math
        bob_y = int(math.sin(self.time * 4.0) * max(1, target_h * 0.01))

        # Posición: centro inferior con leve offset
        anchor = getattr(Config, 'HUD_HANDS_ANCHOR', 'center')
        if anchor == 'right':
            overflow = int(getattr(Config, 'HUD_HANDS_RIGHT_OVERFLOW', 0))
            x = sw - target_w + overflow
        elif anchor == 'left':
            left_off = int(getattr(Config, 'HUD_HANDS_LEFT_OFFSET', 0))
            x = 0 + left_off
        else:
            x = (sw - target_w) // 2 + int(getattr(Config, 'HUD_HANDS_CENTER_OFFSET_X', 0))
        y = sh - target_h - int(getattr(Config, 'HUD_HANDS_BOTTOM_OFFSET', 10)) + bob_y

        screen.blit(sprite, (x, y))
