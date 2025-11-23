"""
Administrador de texturas de paredes.
Carga todas las texturas desde disco al iniciar y entrega fallbacks
si falta algún archivo. Usa caché en memoria y placeholders magenta.
"""
import os
import pygame
from src.game.config import Config
from src.utils.loader import load_image


class TextureManager:
    """
    Gestiona la carga y el acceso a texturas de paredes.

    - load_all_textures(): precarga todas las texturas definidas en el mapa.
    - get_texture(wall_type): retorna la superficie para el tipo dado.
    - set_texture_for_type(): permite sustituir/forzar una textura (p.ej. pared destruida).
    """

    def __init__(self, texture_map=None, base_path=None, texture_size=None):
        self.texture_map = texture_map or {}
        self.base_path = base_path or Config.WALL_TEXTURES_PATH
        self.texture_size = texture_size or Config.TEXTURE_SIZE
        self.cache = {}
        self.placeholder = self._make_placeholder()

    def _make_placeholder(self):
        """Crea una textura magenta del tamaño configurado."""
        size = max(1, int(self.texture_size))
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 255))
        return surf

    def _load_texture_file(self, filename):
        """Carga un archivo desde base_path o retorna placeholder en error."""
        path = os.path.join(self.base_path, filename)
        if not os.path.exists(path):
            return self.placeholder
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return self.placeholder

    def load_all_textures(self):
        """Precarga todas las texturas declaradas en texture_map."""
        for wall_type, filename in self.texture_map.items():
            self.cache[wall_type] = self._load_texture_file(filename)
        return self.cache

    def get_texture(self, wall_type):
        """Devuelve la textura para wall_type o placeholder si no existe."""
        return self.cache.get(wall_type) or self.placeholder

    def set_texture_for_type(self, wall_type, texture_or_name):
        """
        Sustituye la textura de un tipo de pared.
        Acepta una Surface o el nombre de archivo dentro de base_path.
        """
        if isinstance(texture_or_name, pygame.Surface):
            self.cache[wall_type] = texture_or_name.convert_alpha()
        elif isinstance(texture_or_name, str):
            self.cache[wall_type] = self._load_texture_file(texture_or_name)
        else:
            self.cache[wall_type] = self.placeholder

