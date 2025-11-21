"""
Hechizo: Rayo (efecto casi instantáneo). Para simplicidad, crea un trazo breve.
"""
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
            lifetime=0.15,
            color=(120, 200, 255),
        )

    def update(self, dt: float, context):
        # No se mueve; sirve como efecto visual breve
        super().update(dt, context)

