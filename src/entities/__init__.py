"""
Game entities package.

Exports the main subpackages (player, enemies, spells, particles) without
forcing eager imports that might create circular dependencies.
"""

__all__ = ["player", "enemies", "spells", "particles"]
