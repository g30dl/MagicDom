"""
Hechizo: Escarcha (proyectil pequeño que congela al impactar).
Aplica daño frost y congela al enemigo durante 2s.
"""
import math
from src.game.config import Config
from .spell_base import SpellBase


class Frost(SpellBase):
    def __init__(self, x: float, y: float, angle: float):
        super().__init__(
            name="frost",
            x=x,
            y=y,
            angle=angle,
            speed=2.8,
            damage=15,
            lifetime=3.0,
            color=(120, 200, 255),
        )
        self.radius = 6

    def update(self, dt: float, context):
        if not self.alive:
            return
        super().update(dt, context)
        if not self.alive:
            return

        # Avanzar
        self.x += math.cos(self.angle) * self.speed * dt * 100
        self.y += math.sin(self.angle) * self.speed * dt * 100

        # Colisión con paredes
        game_map = context.get("game_map")
        if game_map is not None:
            col = int(self.x // Config.TILE_SIZE)
            row = int(self.y // Config.TILE_SIZE)
            if row < 0 or row >= len(game_map) or col < 0 or col >= len(game_map[0]) or game_map[row][col] != 0:
                return self.on_hit_wall(context)

        # Colisión con enemigos
        enemies = context.get("enemies") or []
        for enemy in enemies:
            if not getattr(enemy, "alive", True):
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            if (dx * dx + dy * dy) <= (self.radius * self.radius * 4):
                return self.on_hit_enemy(enemy, context)

    def on_hit_wall(self, context):
        particles = context.get("particles")
        if particles:
            particles.spawn_spark(self.x, self.y, color=self.color, count=8)
        snd = context.get("sound")
        if snd:
            snd.play_sfx("frost")
        self.alive = False

    def on_hit_enemy(self, enemy, context):
        try:
            enemy.take_damage(self.damage, damage_type=self.name)
        except Exception:
            pass
        particles = context.get("particles")
        if particles:
            particles.spawn_damage_number(enemy.x, enemy.y, self.damage)
            particles.spawn_spark(self.x, self.y, color=self.color, count=12)
        snd = context.get("sound")
        if snd:
            snd.play_sfx("frost")
        self.alive = False
