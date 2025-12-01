"""
Administrador del mapa de juego.
Contiene el layout por defecto y lo expone a los sistemas que lo usan.
"""


DEFAULT_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0 ,0 ,9, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 4, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 9, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1],
    [1, 1, 1, 1, 1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1 ,1, 1 ,1 ,1 ,1 ,4 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,1],
    [1, 0, 0 ,0 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,0 ,1 ,1 ,0 ,0 ,0 ,1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


class MapManager:
    """Gestiona el mapa activo del juego."""

    def __init__(self, map_data=None):
        self.map = [row[:] for row in (map_data or DEFAULT_MAP)]
        self.enemy_spawns = self._extract_enemy_spawns()
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height else 0

    def get_map(self):
        """Retorna la matriz del mapa actual."""
        return self.map

    def get_enemy_spawns(self):
        """Retorna lista de spawns marcados en el mapa como celdas 9 (col, row)."""
        return self.enemy_spawns

    def get_dimensions(self):
        return self.width, self.height

    def get_wall_at(self, x, y):
        """Retorna el tipo de pared en coordenadas de celda (x, y)."""
        col = int(x)
        row = int(y)
        if 0 <= col < self.width and 0 <= row < self.height:
            return self.map[row][col]
        return 1

    def _extract_enemy_spawns(self):
        """
        Busca celdas con valor 9, las guarda como posiciones de spawn
        y las convierte en 0 (suelo) para que no bloqueen el paso.
        """
        spawns = []
        for row_idx, row in enumerate(self.map):
            for col_idx, cell in enumerate(row):
                if cell == 9:
                    spawns.append((col_idx, row_idx))
                    row[col_idx] = 0
        return spawns
