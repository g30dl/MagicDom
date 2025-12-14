"""
Hechizo: Aumento de velocidad (boost temporal).
Aplica un multiplicador de velocidad al jugador durante unos segundos.
"""
from .spell_base import SpellBase


class SpeedBoost(SpellBase):
    def __init__(self, x: float, y: float, angle: float, multiplier: float = 1.6, duration: float = 5.0):
        super().__init__(
            name="speed",
            x=x,
            y=y,
            angle=angle,
            speed=0.0,
            damage=0,
            lifetime=0.1,
            color=(120, 180, 255),
        )
        self.multiplier = float(multiplier)
        self.duration = float(duration)

    def update(self, dt: float, context):
        player = context.get('player')
        if player is not None:
            try:
                player.apply_speed_boost(self.multiplier, self.duration)
            except Exception:
                pass
        self.alive = False
