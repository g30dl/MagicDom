"""
Gestor de hechizos activos. Auto-aim opcional hacia enemigos cercanos.
"""
import math
from typing import List
from src.game.config import Config
from .fireball import Fireball
from .lightning import Lightning
from .frost import Frost
from .healing import Healing
from .speed_boost import SpeedBoost


class SpellManager:
    def __init__(self, game_map, player, particle_manager=None, sound_manager=None):
        self.active_spells: List = []
        self.game_map = game_map
        self.player = player
        self.particles = particle_manager
        self.sound = sound_manager
        self._last_enemies: List = []

    def _pick_auto_aim_angle(self):
        """
        Devuelve el ángulo hacia el enemigo más cercano dentro del FOV.
        Retorna None si no hay objetivo válido.
        """
        if not self._last_enemies:
            return None
        best_angle = None
        best_dist_sq = None
        px, py = self.player.x, self.player.y
        for enemy in self._last_enemies:
            if not getattr(enemy, "alive", True):
                continue
            dx = enemy.x - px
            dy = enemy.y - py
            dist_sq = dx * dx + dy * dy
            angle_to = math.atan2(dy, dx)
            angle_diff = (angle_to - self.player.angle + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > getattr(Config, "HALF_FOV", math.pi / 6):
                continue
            if best_angle is None or dist_sq < best_dist_sq:
                best_angle = angle_to
                best_dist_sq = dist_sq
        return best_angle

    def cast_spell(self, spell_name: str):
        if not spell_name:
            return None

        # Easter egg: matar todo al decir "muere"
        if spell_name == "easter_kill":
            self._kill_all_enemies()
            return None

        # Solo un hechizo activo a la vez (según petición)
        if self.active_spells:
            return None

        # Auto-aim desactivado: usa siempre el ángulo actual del jugador
        angle = self.player.angle
        spawn_offset = getattr(self.player, "collision_radius", 20) * 1.5
        x = self.player.x + math.cos(angle) * spawn_offset
        y = self.player.y + math.sin(angle) * spawn_offset

        spell = None
        if spell_name == "fireball":
            spell = Fireball(x, y, angle)
        elif spell_name == "lightning":
            spell = Lightning(x, y, angle)
        elif spell_name == "frost":
            spell = Frost(x, y, angle)
        elif spell_name == "healing":
            spell = Healing(x, y, angle)
        elif spell_name == "speed":
            spell = SpeedBoost(x, y, angle)

        if spell is not None:
            self.active_spells.append(spell)
            if self.sound:
                self.sound.play_sfx(spell_name)
        return spell

    def _kill_all_enemies(self):
        """Mata a todos los enemigos conocidos (easter egg)."""
        if not self._last_enemies:
            return
        for enemy in list(self._last_enemies):
            try:
                if getattr(enemy, "alive", False):
                    enemy.die()
            except Exception:
                continue
        if self.sound:
            try:
                self.sound.play_sfx("lightning")
            except Exception:
                pass

    def update(self, dt: float, enemies=None):
        context = {
            'game_map': self.game_map,
            'player': self.player,
            'particles': self.particles,
            'enemies': enemies or [],
            'sound': self.sound,
        }
        self._last_enemies = context['enemies']
        for s in list(self.active_spells):
            s.update(dt, context)
        self.active_spells = [s for s in self.active_spells if getattr(s, 'alive', False)]

    def get_active_spells(self):
        return self.active_spells
