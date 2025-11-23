"""
Motor de raycasting con DDA para mejor rendimiento y fidelidad.
Similar al usado en Wolfenstein 3D y DOOM.
"""
import math
from src.game.config import Config


class RayCaster:
    def __init__(self, game_map):
        # game_map: matriz 2D donde 0 = espacio vacío, >0 = pared
        self.map = game_map
        self.map_width = len(game_map[0])
        self.map_height = len(game_map)

    def cast_rays(self, player_x, player_y, player_angle):
        """
        Lanza rayos desde la posición del jugador.
        Retorna lista de (distancia, tipo_pared, hit_x, hit_y, side)
        """
        rays = []

        ray_angle = player_angle - Config.HALF_FOV
        for _ in range(Config.NUM_RAYS):
            distance, wall_type, hit_x, hit_y, side = self.cast_single_ray(
                player_x, player_y, ray_angle
            )
            # Corrección de ojo de pez
            distance *= math.cos(player_angle - ray_angle)
            rays.append((distance, wall_type, hit_x, hit_y, side))
            ray_angle += Config.DELTA_ANGLE

        return rays

    def cast_single_ray(self, ox, oy, angle):
        """
        Lanza un solo rayo desde (ox, oy) en la dirección angle.
        Usa DDA para saltar de celda en celda.
        Retorna (distancia, tipo_pared, hit_x, hit_y, side)
        """
        tile = Config.TILE_SIZE
        ray_dir_x = math.cos(angle)
        ray_dir_y = math.sin(angle)

        map_x = int(ox // tile)
        map_y = int(oy // tile)

        delta_dist_x = float("inf") if ray_dir_x == 0 else abs(tile / ray_dir_x)
        delta_dist_y = float("inf") if ray_dir_y == 0 else abs(tile / ray_dir_y)

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (ox - map_x * tile) / abs(ray_dir_x)
        else:
            step_x = 1
            side_dist_x = ((map_x + 1) * tile - ox) / abs(ray_dir_x)

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (oy - map_y * tile) / abs(ray_dir_y)
        else:
            step_y = 1
            side_dist_y = ((map_y + 1) * tile - oy) / abs(ray_dir_y)

        max_depth = Config.MAX_DEPTH
        side = 0
        perp_dist = 0.0

        while perp_dist < max_depth:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
                perp_dist = side_dist_x - delta_dist_x
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                perp_dist = side_dist_y - delta_dist_y

            # Fuera de límites
            if map_x < 0 or map_x >= self.map_width or map_y < 0 or map_y >= self.map_height:
                hit_x = ox + ray_dir_x * max_depth
                hit_y = oy + ray_dir_y * max_depth
                return (max_depth, 0, hit_x, hit_y, side)

            wall_type = self.map[map_y][map_x]
            if wall_type > 0:
                hit_x = ox + ray_dir_x * perp_dist
                hit_y = oy + ray_dir_y * perp_dist
                return (perp_dist, wall_type, hit_x, hit_y, side)

        hit_x = ox + ray_dir_x * max_depth
        hit_y = oy + ray_dir_y * max_depth
        return (max_depth, 0, hit_x, hit_y, side)

    def get_wall_at(self, x, y):
        """Obtiene el tipo de pared en la posición (x, y)"""
        col = int(x // Config.TILE_SIZE)
        row = int(y // Config.TILE_SIZE)

        if 0 <= col < self.map_width and 0 <= row < self.map_height:
            return self.map[row][col]
        return 1  # Fuera de límites = pared


# Mapa 
EXAMPLE_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0 ,0 ,0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 4, 3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 3, 3, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
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
