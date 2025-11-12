"""
Motor de raycasting
Implementación del algoritmo de raycasting para renderizado pseudo-3D
Similar al usado en Wolfenstein 3D y DOOM
"""
import math
from src.game.config import Config

class RayCaster:
    # Inicializa el raycaster con el mapa del juego
    def __init__(self, game_map):
        # game_map: matriz 2D donde 0 = espacio vacío, >0 = pared
        self.map = game_map
        self.map_width = len(game_map[0])
        self.map_height = len(game_map)
    
    def cast_rays(self, player_x, player_y, player_angle):
        '''
        Lanza rayos desde la posición del jugador
        Retorna lista de (distancia, tipo_pared, hit_x, hit_y) para cada rayo
        '''
        rays = []
        
        # Ángulo inicial
        ray_angle = player_angle - Config.HALF_FOV
        
        for ray in range(Config.NUM_RAYS):
            # Lanzar rayo
            distance, wall_type, hit_x, hit_y = self.cast_single_ray(
                player_x, player_y, ray_angle
            )
            
            # Corrección de ojo de pez
            distance *= math.cos(player_angle - ray_angle)
            
            rays.append((distance, wall_type, hit_x, hit_y))
            
            # Incrementar ángulo para siguiente rayo
            ray_angle += Config.DELTA_ANGLE
        
        return rays
    
    def cast_single_ray(self, ox, oy, angle):
        """
        Lanza un solo rayo desde (ox, oy) en la dirección angle
        Retorna (distancia, tipo_pared, hit_x, hit_y)
        """
        sin_a = math.sin(angle)
        cos_a = math.cos(angle)
        
        # Convertir posición del jugador a coordenadas del mapa
        map_x = int(ox // Config.TILE_SIZE)
        map_y = int(oy // Config.TILE_SIZE)
        
        # Dirección del rayo
        dx = cos_a
        dy = sin_a
        
        # Distancia recorrida
        distance = 0
        
        # Lanzar rayo hasta golpear pared o alcanzar distancia máxima
        while distance < Config.MAX_DEPTH:
            distance += 1
            
            # Nueva posición del rayo
            target_x = ox + dx * distance
            target_y = oy + dy * distance
            
            # Convertir a coordenadas del mapa
            col = int(target_x // Config.TILE_SIZE)
            row = int(target_y // Config.TILE_SIZE)
            
            # Verificar límites del mapa
            if not (0 <= col < self.map_width and 0 <= row < self.map_height):
                return (Config.MAX_DEPTH, 0, target_x, target_y)
            
            # Verificar colisión con pared
            wall_type = self.map[row][col]
            if wall_type > 0:
                return (distance, wall_type, target_x, target_y)
        
        # No se encontró pared
        return (Config.MAX_DEPTH, 0, ox + dx * Config.MAX_DEPTH, oy + dy * Config.MAX_DEPTH)
    
    def get_wall_at(self, x, y):
        """Obtiene el tipo de pared en la posición (x, y)"""
        col = int(x // Config.TILE_SIZE)
        row = int(y // Config.TILE_SIZE)
        
        if 0 <= col < self.map_width and 0 <= row < self.map_height:
            return self.map[row][col]
        return 1  # Fuera de límites = pared


# Mapa de ejemplo para pruebas
EXAMPLE_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 3, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 2, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]