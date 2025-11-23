"""
Sistema de renderizado.
Dibuja la vista 3D usando raycasting y texturas estilo DOOM.
"""
import math
import pygame
from src.game.config import Config
from src.rendering.raycaster import RayCaster, EXAMPLE_MAP
from src.rendering.texture_manager import TextureManager


class Renderer:
    def __init__(self, screen):
        """Inicializa renderer y precarga texturas de pared."""
        self.screen = screen
        self.raycaster = RayCaster(EXAMPLE_MAP)

        self.texture_manager = TextureManager(
            texture_map=Config.WALL_TEXTURE_MAP,
            base_path=Config.WALL_TEXTURES_PATH,
            texture_size=Config.TEXTURE_SIZE,
        )
        self.texture_manager.load_all_textures()

        # Colores de respaldo (minimapa y fallback sin textura)
        self.wall_colors = {
            1: (100, 100, 100),
            2: (150, 75, 0),
            3: (0, 100, 150),
            4: (180, 120, 40),
        }

        self.column_width = Config.SCREEN_WIDTH / Config.NUM_RAYS
        self._last_rays = None

    def render_3d_view(self, player):
        """Renderiza la vista 3D desde la perspectiva del jugador."""
        shear_factor = getattr(Config, "PITCH_SHEAR_FACTOR", 0.25)
        try:
            shear_offset = math.tan(getattr(player, "pitch", 0.0)) * (Config.SCREEN_HEIGHT * shear_factor)
        except Exception:
            shear_offset = 0
        horizon = int((Config.SCREEN_HEIGHT // 2) + shear_offset)
        horizon = max(0, min(Config.SCREEN_HEIGHT, horizon))

        # Cielo y piso
        pygame.draw.rect(self.screen, (50, 50, 100), (0, 0, Config.SCREEN_WIDTH, horizon))
        pygame.draw.rect(self.screen, (30, 30, 30), (0, horizon, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT - horizon))

        rays = self.raycaster.cast_rays(player.x, player.y, player.angle)
        self._last_rays = rays

        for i, (distance, wall_type, hit_x, hit_y, side) in enumerate(rays):
            if wall_type == 0:
                continue

            min_dist = max(distance, Config.TILE_SIZE * 0.05)
            wall_height = (Config.TILE_SIZE * Config.SCREEN_HEIGHT) / min_dist

            top = max(0, int(horizon - wall_height // 2))
            bottom = min(Config.SCREEN_HEIGHT, int(top + wall_height))
            column_height = int(bottom - top)
            if column_height <= 0:
                continue

            texture = self.texture_manager.get_texture(wall_type)

            tex_coord = hit_y if side == 0 else hit_x
            tex_normalized = (tex_coord % Config.TILE_SIZE) / Config.TILE_SIZE
            tex_x = int(tex_normalized * texture.get_width())
            tex_x = max(0, min(texture.get_width() - 1, tex_x))

            tex_column = texture.subsurface((tex_x, 0, 1, texture.get_height()))
            scaled_column = pygame.transform.scale(tex_column, (int(self.column_width) + 2, column_height))

            shade_factor = max(0.2, 1 - (min_dist / Config.MAX_DEPTH))
            if side == 1:
                shade_factor *= 0.75

            shade_value = max(0, min(255, int(255 * shade_factor)))
            x = i * self.column_width
            try:
                shaded = scaled_column.copy()
                shaded.fill(
                    (shade_value, shade_value, shade_value, 255),
                    special_flags=pygame.BLEND_RGBA_MULT
                )
                self.screen.blit(shaded, (int(x), int(top)))
            except Exception:
                base_color = self.wall_colors.get(wall_type, Config.GRAY)
                color = tuple(int(c * shade_factor) for c in base_color)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x, top, self.column_width + 1, bottom - top)
                )

    def render_crosshair(self, size: int = 3, color=Config.WHITE):
        """Dibuja un punto de mira simple en el centro de la pantalla."""
        cx = Config.SCREEN_WIDTH // 2
        cy = Config.SCREEN_HEIGHT // 2
        try:
            pygame.draw.circle(self.screen, color, (cx, cy), max(1, int(size)))
        except Exception:
            pass

    def render_spells_3d(self, player, spells):
        """
        Dibuja hechizos como sprites billboard simples con oclusión básica.
        """
        if not spells:
            return
        if not self._last_rays:
            return

        shear_factor = getattr(Config, "PITCH_SHEAR_FACTOR", 0.25)
        try:
            shear_offset = math.tan(getattr(player, "pitch", 0.0)) * (Config.SCREEN_HEIGHT * shear_factor)
        except Exception:
            shear_offset = 0
        horizon = int((Config.SCREEN_HEIGHT // 2) + shear_offset)

        for s in spells:
            try:
                dx = s.x - player.x
                dy = s.y - player.y
                distance = max(1.0, (dx*dx + dy*dy) ** 0.5)

                angle_to = math.atan2(dy, dx)
                angle_diff = (angle_to - player.angle + math.pi) % (2 * math.pi) - math.pi

                if abs(angle_diff) > Config.HALF_FOV:
                    continue

                ray_index_f = (angle_diff + Config.HALF_FOV) / Config.DELTA_ANGLE
                ray_index = int(max(0, min(Config.NUM_RAYS - 1, ray_index_f)))

                wall_dist = self._last_rays[ray_index][0]
                if distance > wall_dist:
                    continue

                sprite_h = (Config.TILE_SIZE * Config.SCREEN_HEIGHT) / distance
                radius = int(max(3, sprite_h * 0.15))

                screen_x = int((ray_index_f / Config.NUM_RAYS) * Config.SCREEN_WIDTH)
                screen_y = horizon

                color = getattr(s, 'color', (255, 200, 50))
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
            except Exception:
                continue

    def render_minimap(self, player, position=(10, 10), scale=5, spells=None, particles=None):
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
                    pygame.draw.rect(
                        minimap_surface,
                        (20, 20, 20),
                        (col * scale, row * scale, scale, scale)
                    )
        
        player_map_x = int(player.x // Config.TILE_SIZE * scale)
        player_map_y = int(player.y // Config.TILE_SIZE * scale)
        
        collision_radius_scaled = int(player.collision_radius / Config.TILE_SIZE * scale)
        pygame.draw.circle(
            minimap_surface,
            (100, 100, 255, 100),
            (player_map_x, player_map_y),
            collision_radius_scaled,
            1
        )
        
        pygame.draw.circle(
            minimap_surface,
            Config.YELLOW,
            (player_map_x, player_map_y),
            4
        )
        
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
        
        try:
            if spells:
                from src.rendering.spell_renderer import SpellRenderer
                SpellRenderer().render_on_minimap(minimap_surface, spells, scale)
            if particles:
                from src.rendering.particle_renderer import ParticleRenderer
                ParticleRenderer().render_on_minimap(minimap_surface, particles, scale)
        except Exception:
            pass
        
        pygame.draw.rect(
            minimap_surface,
            Config.WHITE,
            (0, 0, minimap_surface.get_width(), minimap_surface.get_height()),
            2
        )
        
        self.screen.blit(minimap_surface, position)

