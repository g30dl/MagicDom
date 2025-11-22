"""
Gestor de hechizos activos. Permite castear por nombre y actualiza sus efectos.
"""
from typing import List
from .fireball import Fireball
from .lightning import Lightning
from .frost import Frost
from .healing import Healing


class SpellManager:
    def __init__(self, game_map, player, particle_manager=None, sound_manager=None):
        self.active_spells: List = []
        self.game_map = game_map
        self.player = player
        self.particles = particle_manager
        self.sound = sound_manager

    def cast_spell(self, spell_name: str):
        if not spell_name:
            return None

        # Solo un hechizo activo a la vez (según petición)
        if self.active_spells:
            return None

        x, y = self.player.x, self.player.y
        angle = self.player.angle

        spell = None
        if spell_name == "fireball":
            spell = Fireball(x, y, angle)
        elif spell_name == "lightning":
            spell = Lightning(x, y, angle)
        elif spell_name == "frost":
            spell = Frost(x, y, angle)
        elif spell_name == "healing":
            spell = Healing(x, y, angle)

        if spell is not None:
            self.active_spells.append(spell)
            if self.sound:
                self.sound.play_sfx(spell_name)
        return spell

    def update(self, dt: float, enemies=None):
        context = {
            'game_map': self.game_map,
            'player': self.player,
            'particles': self.particles,
            'enemies': enemies or [],
            'sound': self.sound,
        }
        for s in list(self.active_spells):
            s.update(dt, context)
        # Limpiar muertos
        self.active_spells = [s for s in self.active_spells if getattr(s, 'alive', False)]

    def get_active_spells(self):
        return self.active_spells
