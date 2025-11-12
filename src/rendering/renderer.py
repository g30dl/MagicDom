"""
Sistema de renderizado
Dibuja la vista 3D usando los resultados del raycasting
"""
import pygame
import math
from src.game.config import Config
from src.rendering.raycaster import RayCaster, EXAMPLE_MAP

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.raycaster = RayCaster(EXAMPLE_MAP)
        
        # Colores para diferentes tipos de paredes
        self.wall_colors = {
            1: (100, 100, 100),  # Gris
            2: (150, 75, 0),     # Marrón
            3: (0, 100, 150),    # Azul oscuro
        }
        
        # Calcular ancho de cada columna
        self.column_width = Config.SCREEN_WIDTH / Config.NUM_RAYS
    
    def render_3d_view(self, player):
        """
        Renderiza la vista 3D desde la perspectiva del jugador
        """
        # Dibujar cielo (mitad superior)
        pygame.draw.rect(
            self.screen,
            (50, 50, 100),  # Azul oscuro
            (0, 0, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT // 2)
        )
        
        # Dibujar piso (mitad inferior)
        pygame.draw.rect(
            self.screen,
            (30, 30, 30),  # Gris oscuro
            (0, Config.SCREEN_HEIGHT // 2, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT // 2)
        )
        
        # Obtener rayos
        rays = self.raycaster.cast_rays(player.x, player.y, player.angle)
        
        # Dibujar cada rayo como una columna vertical
        for i, (distance, wall_type, hit_x, hit_y) in enumerate(rays):
            if wall_type == 0:
                continue
            
            # Calcular altura de la pared basado en distancia
            if distance == 0:
                distance = 1
            
            wall_height = (Config.TILE_SIZE * Config.SCREEN_HEIGHT) / distance
            
            # Calcular posición vertical
            top = (Config.SCREEN_HEIGHT - wall_height) // 2
            bottom = top + wall_height
            
            # Limitar al tamaño de pantalla
            if top < 0:
                top = 0
            if bottom > Config.SCREEN_HEIGHT:
                bottom = Config.SCREEN_HEIGHT
            
            # Obtener color de la pared
            base_color = self.wall_colors.get(wall_type, Config.GRAY)
            
            # Aplicar sombreado basado en distancia
            shade_factor = max(0.3, 1 - (distance / Config.MAX_DEPTH))
            color = tuple(int(c * shade_factor) for c in base_color)
            
            # Dibujar columna
            x = i * self.column_width
            pygame.draw.rect(
                self.screen,
                color,
                (x, top, self.column_width + 1, bottom - top)
            )
    
    def render_minimap(self, player, position=(10, 10), scale=5):
        """
        Renderiza un minimapa en 2D con radio de colisión visible
        """
        minimap_surface = pygame.Surface(
            (len(self.raycaster.map[0]) * scale, len(self.raycaster.map) * scale)
        )
        minimap_surface.fill(Config.BLACK)
        minimap_surface.set_alpha(200)  # Semi-transparente
        
        # Dibujar mapa
        for row in range(len(self.raycaster.map)):
            for col in range(len(self.raycaster.map[0])):
                if self.raycaster.map[row][col] > 0:
                    wall_type = self.raycaster.map[row][col]
                    color = self.wall_colors.get(wall_type, Config.WHITE)
                    pygame.draw.rect(
                        minimap_surface,
                        color,
                        (col * scale, row * scale, scale, scale)
                    )
                else:
                    # Dibujar piso con color más oscuro
                    pygame.draw.rect(
                        minimap_surface,
                        (20, 20, 20),
                        (col * scale, row * scale, scale, scale)
                    )
        
        # Calcular posición del jugador en el minimap
        player_map_x = int(player.x // Config.TILE_SIZE * scale)
        player_map_y = int(player.y // Config.TILE_SIZE * scale)
        
        # Dibujar radio de colisión del jugador
        collision_radius_scaled = int(player.collision_radius / Config.TILE_SIZE * scale)
        pygame.draw.circle(
            minimap_surface,
            (100, 100, 255, 100),  # Azul semi-transparente
            (player_map_x, player_map_y),
            collision_radius_scaled,
            1
        )
        
        # Dibujar jugador
        pygame.draw.circle(
            minimap_surface,
            Config.YELLOW,
            (player_map_x, player_map_y),
            4
        )
        
        # Dibujar dirección del jugador
        dir_length = 15
        end_x = player_map_x + int(math.cos(player.angle) * dir_length)
        end_y = player_map_y + int(math.sin(player.angle) * dir_length)
        pygame.draw.line(
            minimap_surface,
            Config.RED,
            (player_map_x, player_map_y),
            (end_x, end_y),
            2
        )
        
        # Dibujar borde del minimap
        pygame.draw.rect(
            minimap_surface,
            Config.WHITE,
            (0, 0, minimap_surface.get_width(), minimap_surface.get_height()),
            2
        )
        
        self.screen.blit(minimap_surface, position)