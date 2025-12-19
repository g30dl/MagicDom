"""
Administrador del mapa de juego.
Contiene el layout por defecto y lo expone a los sistemas que lo usan.
"""


DEFAULT_MAP = [
 
    [1, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 4, 0, 0, 5, 2, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 0, 2, 2, 3, 4, 1, 2, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 1],
    [1, 0, 2, 2, 5, 0, 1, 2, 0, 0, 0, 0, 9, 3, 0, 0, 0, 3, 3, 0, 0, 3, 0, 0, 1],
    [1, 0, 2, 2, 5, 0, 2, 2, 0, 0, 0, 0, 0, 3, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 1],
    [5, 0, 2, 2, 5, 0, 4, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 2, 2, 3, 3, 3, 3, 3, 2, 2, 1, 4, 1, 3, 3, 2, 2, 1, 1, 3, 3, 3, 2, 2, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 9, 1],
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]
 
# Mensajes asociados a carteles (tile tipo 5)
SIGN_TEXTS = {
    (1, 0): "Invoca hechizos mencionando su nombre. Destruye paredes con fuego (“bola de fuego”,"
    " “fuego”, “fireball” )",
    (0, 5): "¡Bienvenido a MagicDom!. Usa WASD + mouse para moverte",
    (6, 1): "Algunos enemigos son vulnerables a hechizos específicos.",
    (4, 3): "Utiliza Heal (curar”, “heal”, “healing) para restaurar tu salud si "
    "lo necesitas. Prueba yendo más rapido con velocidad (“velocidad”, “rapidez”, “speed”)",
    (4, 4): "Congela (“hielo”, “congelar”, “freeze”, “frost” ) a tus enemigos con hielo "
    "para ralentizarlos.",
    (4, 5): "Tira rayos (“rayo”, “trueno”, “relámpago”, “lightning”) para ser mas "
    "poderoso contra enemigos en grupo",

}

class MapManager:
    """Gestiona el mapa activo del juego."""

    def __init__(self, map_data=None):
        self.map = [row[:] for row in (map_data or DEFAULT_MAP)]
        self.enemy_spawns, self.boss_spawns = self._extract_enemy_spawns()
        self.signs = self._extract_signs()
        self.height = len(self.map)
        self.width = len(self.map[0]) if self.height else 0

    def get_map(self):
        """Retorna la matriz del mapa actual."""
        return self.map

    def get_enemy_spawns(self):
        """Retorna lista de spawns marcados en el mapa como celdas 9 (col, row)."""
        return self.enemy_spawns

    def get_boss_spawns(self):
        """Retorna lista de spawns marcados en el mapa como celdas 8 (col, row)."""
        return self.boss_spawns

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
        Busca celdas con valor 9 (enemigos) y 8 (boss),
        las guarda como posiciones de spawn y las convierte en 0 (suelo)
        para que no bloqueen el paso.
        """
        spawns = []
        boss_spawns = []
        for row_idx, row in enumerate(self.map):
            for col_idx, cell in enumerate(row):
                if cell == 9:
                    spawns.append((col_idx, row_idx))
                    row[col_idx] = 0
                elif cell == 8:
                    boss_spawns.append((col_idx, row_idx))
                    row[col_idx] = 0
        return spawns, boss_spawns

    def _extract_signs(self):
        """
        Busca celdas con valor 5 y registra un mensaje opcional.
        Los carteles permanecen como paredes (no se convierten en suelo).
        """
        signs = {}
        for row_idx, row in enumerate(self.map):
            for col_idx, cell in enumerate(row):
                if cell == 5:
                    msg = SIGN_TEXTS.get((col_idx, row_idx), "Cartel sin mensaje.")
                    signs[(col_idx, row_idx)] = msg
        return signs
