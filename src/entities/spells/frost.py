"""
Hechizo: Escarcha (proyectil lento). Stub básico.
"""
import math
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
        self.x += math.cos(self.angle) * self.speed * dt * 100
        self.y += math.sin(self.angle) * self.speed * dt * 100

