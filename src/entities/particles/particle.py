"""
Entidad de partícula simple.
"""
import random


class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color=(255, 200, 50), lifetime: float = 0.6, size: int = 3):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color = color
        self.lifetime = float(lifetime)
        self.size = int(size)
        self.alive = True

    def update(self, dt: float):
        if not self.alive:
            return
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.alive = False
            return
        # Movimiento y leve amortiguación
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.98
        self.vy *= 0.98

