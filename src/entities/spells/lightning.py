"""
Hechizo: Rayo. Golpea hasta 4 tiles libres frente al jugador con rayos instantáneos.
Se detiene al topar con una pared.
"""
import math
from src.game.config import Config
from .spell_base import SpellBase


class Lightning(SpellBase):
    def __init__(self, x: float, y: float, angle: float):
        super().__init__(
            name="lightning",
            x=x,
            y=y,
            angle=angle,
            speed=0.0,
            damage=35,
            lifetime=1.0,
            color=(255, 220, 80),
        )
        self.strike_points = []
        self.active_strikes = []
        self._scheduled = []
        self._triggered = False
        self._elapsed = 0.0

    def _compute_strikes(self, context):
        player = context.get("player")
        game_map = context.get("game_map")
        if player is None or game_map is None:
            return

        px, py = player.x, player.y
        angle = getattr(player, "angle", self.angle)
        max_steps = 4
        for step in range(1, max_steps + 1):
            dist = Config.TILE_SIZE * step
            sx = px + math.cos(angle) * dist
            sy = py + math.sin(angle) * dist
            col = int(sx // Config.TILE_SIZE)
            row = int(sy // Config.TILE_SIZE)
            if row < 0 or row >= len(game_map) or col < 0 or col >= len(game_map[0]):
                break
            if game_map[row][col] != 0:
                break  # pared encontrada
            cx = col * Config.TILE_SIZE + Config.TILE_SIZE * 0.5
            cy = row * Config.TILE_SIZE + Config.TILE_SIZE * 0.5
            self.strike_points.append((cx, cy))
        # Programar impactos secuenciales (cada 0.15s)
        delay_step = 0.15
        self._scheduled = [
            {"point": p, "delay": i * delay_step, "done": False}
            for i, p in enumerate(self.strike_points)
        ]

    def _apply_damage(self, context, point):
        enemies = context.get("enemies") or []
        if not enemies:
            return
        radius = Config.TILE_SIZE * 0.6
        radius_sq = radius * radius
        cx, cy = point
        for enemy in enemies:
            if not getattr(enemy, "alive", True):
                continue
            dx = enemy.x - cx
            dy = enemy.y - cy
            if (dx * dx + dy * dy) <= radius_sq:
                try:
                    enemy.take_damage(self.damage, damage_type=self.name)
                    particles = context.get("particles")
                    if particles:
                        particles.spawn_damage_number(enemy.x, enemy.y, self.damage)
                except Exception:
                    pass

    def _spawn_fx(self, context, point):
        particles = context.get("particles")
        if particles:
            cx, cy = point
            particles.spawn_spark(cx, cy, color=(180, 220, 255), count=10)
        snd = context.get("sound")
        if snd:
            snd.play_sfx("lightning")

    def update(self, dt: float, context):
        if not self._triggered:
            self._compute_strikes(context)
            self._triggered = True

        # Crono de golpes secuenciales
        self._elapsed += dt
        for item in self._scheduled:
            if item["done"]:
                continue
            if self._elapsed >= item["delay"]:
                pt = item["point"]
                self.active_strikes.append(pt)
                self._apply_damage(context, pt)
                self._spawn_fx(context, pt)
                item["done"] = True

        super().update(dt, context)
