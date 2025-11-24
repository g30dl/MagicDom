"""
Administrador de texturas de paredes.
Carga todas las texturas desde disco al iniciar y entrega fallbacks
si falta algún archivo. Usa caché en memoria y placeholders magenta.
"""
import os
import pygame
from collections import OrderedDict
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
        self.column_cache = OrderedDict()
        self.max_column_cache = 512
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

    def get_scaled_column(self, wall_type, tex_x, column_height, column_width, texture=None):
        """
        Devuelve una columna de textura escalada al alto/ancho solicitados.
        Usa una caché LRU limitada para evitar recalcular columnas.
        """
        texture = texture if texture is not None else self.get_texture(wall_type)
        target_width = max(1, int(column_width))
        target_height = max(1, int(column_height))
        key = (
            int(wall_type),
            int(tex_x),
            target_width,
            target_height,
        )
        cached = self.column_cache.get(key)
        if cached is not None:
            self.column_cache.move_to_end(key)
            return cached
        try:
            src_x = max(0, min(texture.get_width() - 1, int(tex_x)))
            src_height = texture.get_height()
            src_column = texture.subsurface((src_x, 0, 1, src_height))
        except Exception:
            # Fallback a placeholder básico
            placeholder = self.placeholder
            src_height = placeholder.get_height()
            src_column = placeholder.subsurface((0, 0, 1, src_height))

        try:
            scaled = pygame.transform.scale(src_column, (target_width, target_height))
        except Exception:
            # En caso de error de escalado, devolver columna placeholder sin escalar
            scaled = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
            scaled.blit(src_column, (0, 0), area=pygame.Rect(0, 0, 1, min(target_height, src_height)))

        self.column_cache[key] = scaled
        if len(self.column_cache) > self.max_column_cache:
            self.column_cache.popitem(last=False)
        return scaled

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
