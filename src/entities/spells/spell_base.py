"""
Clase base para hechizos.
"""
import math


class SpellBase:
    def __init__(self, name: str, x: float, y: float, angle: float,
                 speed: float = 0.0, damage: int = 10, lifetime: float = 2.0,
                 color=(255, 200, 50)):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.speed = float(speed)
        self.damage = int(damage)
        self.lifetime = float(lifetime)
        self.alive = True
        self.color = color

    def update(self, dt: float, context):
        """
        Actualiza el hechizo. `context` puede incluir referencias como:
        {
          'game_map': [...], 'player': Player, 'particles': ParticleManager
        }
        """
        if not self.alive:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.on_expire(context)
            self.alive = False

    def on_hit_wall(self, context):
        """Llamado al colisionar con una pared."""
        self.alive = False

    def on_expire(self, context):
        """Llamado al expirar la vida del hechizo."""
        pass

    def get_position(self):
        return (self.x, self.y)

