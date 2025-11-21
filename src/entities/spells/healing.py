"""
Hechizo: Sanación (instantáneo). Aumenta salud del jugador.
"""
from .spell_base import SpellBase


class Healing(SpellBase):
    def __init__(self, x: float, y: float, angle: float, amount: int = 20):
        super().__init__(
            name="healing",
            x=x,
            y=y,
            angle=angle,
            speed=0.0,
            damage=0,
            lifetime=0.2,
            color=(120, 255, 120),
        )
        self.amount = int(amount)

    def update(self, dt: float, context):
        player = context.get('player')
        if player is not None:
            player.heal(self.amount)
        self.alive = False

