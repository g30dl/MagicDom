"""
Gestor de partículas y generadores de efectos comunes.
"""
import math
import random
from typing import List
from src.game.config import Config
from .particle import Particle


class ParticleManager:
    def __init__(self):
        self.particles: List[Particle] = []

    def update(self, dt: float):
        for p in list(self.particles):
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        # Evitar crecer sin control
        if len(self.particles) > Config.MAX_PARTICLES:
            overflow = len(self.particles) - Config.MAX_PARTICLES
            del self.particles[0:overflow]

    def get_particles(self):
        return self.particles

    # Efectos
    def spawn_explosion(self, x: float, y: float, color=(255, 180, 80), count: int = 14):
        for _ in range(count):
            angle = random.random() * math.tau
            speed = 50 + random.random() * 120
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = 2 + int(random.random() * 3)
            life = 0.4 + random.random() * 0.5
            self._append_particle(Particle(x, y, vx, vy, color=color, lifetime=life, size=size))

    def spawn_spark(self, x: float, y: float, color=(255, 220, 120), count: int = 6):
        for _ in range(count):
            angle = random.random() * math.tau
            speed = 30 + random.random() * 60
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = 2
            life = 0.2 + random.random() * 0.3
            self._append_particle(Particle(x, y, vx, vy, color=color, lifetime=life, size=size))

    def _append_particle(self, particle: Particle):
        """Append con trim en caso de overflow para proteger FPS."""
        self.particles.append(particle)
        if len(self.particles) > Config.MAX_PARTICLES:
            overflow = len(self.particles) - Config.MAX_PARTICLES
            del self.particles[0:overflow]
