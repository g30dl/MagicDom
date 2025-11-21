"""
Hechizo: Bola de Fuego (proyectil simple con colisión de paredes y partículas al impactar).
"""
import math
from .spell_base import SpellBase
from src.game.config import Config


class Fireball(SpellBase):
    def __init__(self, x: float, y: float, angle: float):
        super().__init__(
            name="fireball",
            x=x,
            y=y,
            angle=angle,
            speed=5.0,
            damage=25,
            lifetime=3.0,
            color=(255, 120, 40),
        )
        self.radius = 8

    def update(self, dt: float, context):
        if not self.alive:
            return
        # Avanzar en línea recta
        self.x += math.cos(self.angle) * self.speed * dt * 100
        self.y += math.sin(self.angle) * self.speed * dt * 100

        # Chequear colisión con pared (tile != 0)
        game_map = context.get('game_map')
        if game_map is not None:
            col = int(self.x // Config.TILE_SIZE)
            row = int(self.y // Config.TILE_SIZE)
            if row < 0 or row >= len(game_map) or col < 0 or col >= len(game_map[0]):
                self.on_hit_wall(context)
                return
            if game_map[row][col] != 0:
                self.on_hit_wall(context)

    def on_hit_wall(self, context):
        particles = context.get('particles')
        if particles is not None:
            particles.spawn_explosion(self.x, self.y, color=(255, 120, 40))
        self.alive = False

    def on_expire(self, context):
        # No expira por tiempo; sólo por colisión
        pass
