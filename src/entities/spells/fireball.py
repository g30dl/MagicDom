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
            damage=40,
            lifetime=3.0,
            color=(255, 120, 40),
        )
        self.radius = 8
        # Velocidad fija en el momento de castear (no sigue rotaciones posteriores)
        self.vx = math.cos(self.angle) * self.speed * 100
        self.vy = math.sin(self.angle) * self.speed * 100

    def update(self, dt: float, context):
        # Consumir lifetime y detener si expiró
        super().update(dt, context)
        if not self.alive:
            return
        # Avanzar en línea recta
        self.x += self.vx * dt
        self.y += self.vy * dt

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
                return

        # Colisión con enemigos si están presentes
        enemies = context.get('enemies') or []
        for enemy in enemies:
            if not getattr(enemy, "alive", True):
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            if (dx * dx + dy * dy) <= (self.radius * self.radius * 4):
                self.on_hit_enemy(enemy, context)
                break

    def on_hit_wall(self, context):
        game_map = context.get('game_map')
        destroyed = False
        if game_map is not None:
            col = int(self.x // Config.TILE_SIZE)
            row = int(self.y // Config.TILE_SIZE)
            # Evitar tocar el borde exterior
            if 0 < row < len(game_map) - 1 and 0 < col < len(game_map[0]) - 1:
                if game_map[row][col] == 4:
                    game_map[row][col] = 0  # Romper pared destructible
                    destroyed = True

        particles = context.get('particles')
        if particles is not None:
            color = (255, 180, 80) if destroyed else (255, 120, 40)
            particles.spawn_explosion(self.x, self.y, color=color)
        # SFX
        snd = context.get('sound')
        if snd:
            if destroyed:
                snd.play_sfx("romper_pared")
            else:
                snd.play_sfx("hit")
        self.alive = False

    def on_hit_enemy(self, enemy, context):
        try:
            enemy.take_damage(self.damage, damage_type=self.name)
            # knockback ligero
            kb = 60
            enemy.x += math.cos(self.angle) * kb
            enemy.y += math.sin(self.angle) * kb
        except Exception:
            pass
        particles = context.get('particles')
        if particles is not None:
            particles.spawn_damage_number(enemy.x, enemy.y, self.damage)
            particles.spawn_explosion(self.x, self.y, color=(255, 80, 40))
        snd = context.get('sound')
        if snd:
            snd.play_sfx("hit")
        self.alive = False

    def on_expire(self, context):
        # Pequeño destello al expirar sin colisión
        particles = context.get('particles')
        if particles is not None:
            particles.spawn_explosion(self.x, self.y, color=(200, 120, 60), count=6)
