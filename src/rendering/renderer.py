"""
Sistema de renderizado.
Dibuja la vista 3D usando raycasting y texturas estilo DOOM.
"""
import math
import os
import pygame
from src.game.config import Config
from src.rendering.raycaster import RayCaster
from src.rendering.texture_manager import TextureManager


class Renderer:
    def __init__(self, screen, map_manager):
        """Inicializa renderer y precarga texturas de pared."""
        self.screen = screen
        self.map_manager = map_manager
        self.raycaster = RayCaster(map_manager.get_map())

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

        self.column_width = max(1, int(math.ceil(Config.SCREEN_WIDTH / Config.NUM_RAYS)))
        self._gradient_cache = {}
        self.skybox = self._load_skybox()
        self.sky_surface = self._load_sky_texture()  # fallback simple

    def _compute_horizon(self, player):
        # Sin pitch: horizonte fijo en el centro de pantalla
        return Config.SCREEN_HEIGHT // 2

    def _draw_background(self, horizon, player):
        if not self._draw_skybox(horizon, player):
            if self.sky_surface is not None:
                try:
                    self.screen.blit(self.sky_surface, (0, 0))
                except Exception:
                    pygame.draw.rect(self.screen, (50, 50, 100), (0, 0, Config.SCREEN_WIDTH, horizon))
            else:
                pygame.draw.rect(self.screen, (50, 50, 100), (0, 0, Config.SCREEN_WIDTH, horizon))
        pygame.draw.rect(self.screen, (30, 30, 30), (0, horizon, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT - horizon))

    def _apply_vertical_shading(self, surface):
        """Aplica un degradado vertical suave (Y-shading)."""
        # Temporal: desactivar gradiente vertical para probar FPS
        return surface

    def render_3d_view(self, player, spells=None):
        """Renderiza la vista 3D desde la perspectiva del jugador."""
        horizon = self._compute_horizon(player)
        self._draw_background(horizon, player)

        rays = self.raycaster.cast_rays(player.x, player.y, player.angle)

        render_queue = []

        for i, ray in enumerate(rays):
            item = self._render_wall_column(ray, i, horizon)
            if item:
                render_queue.append(item)

        if spells:
            render_queue.extend(self._gather_spell_commands(player, spells, horizon, rays))

        render_queue.sort(key=lambda item: item.get("distance", 0), reverse=True)

        for item in render_queue:
            self._draw_render_item(item)

    def _load_sky_texture(self):
        """Carga y escala la textura de cielo si existe."""
        path = os.path.join(Config.WALL_TEXTURES_PATH, "sky.png")
        if not os.path.exists(path):
            return None
        try:
            tex = pygame.image.load(path).convert()
            return pygame.transform.scale(tex, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT // 2))
        except Exception:
            return None

    def _load_skybox(self):
        """
        Carga la imagen panorámica del cielo (360) si existe.
        Busca primero sky_panorama.png y, si no está, intenta usar sky.png como panorámica.
        """
        path = os.path.join(Config.WALL_TEXTURES_PATH, "sky.png")
        try:
            return pygame.image.load(path).convert()
        except Exception:
            return None

    def _draw_skybox(self, horizon, player):
        """Dibuja la porción panorámica del cielo según el ángulo del jugador."""
        if self.skybox is None:
            return False
        try:
            sky = self.skybox
            sky_w = sky.get_width()
            sky_h = sky.get_height()
            if sky_w <= 0 or sky_h <= 0:
                return False

            # Fracción del panorama según el ángulo del jugador
            angle = getattr(player, "angle", 0.0)
            u = (angle % (2 * math.pi)) / (2 * math.pi)
            start_x = int(u * sky_w)
            view_w = Config.SCREEN_WIDTH
            view_h = max(1, horizon)

            # Componer la franja visible (envolviendo si es necesario)
            dest = pygame.Surface((view_w, sky_h)).convert()
            if start_x + view_w <= sky_w:
                dest.blit(sky, (0, 0), area=pygame.Rect(start_x, 0, view_w, sky_h))
            else:
                w1 = sky_w - start_x
                w2 = view_w - w1
                dest.blit(sky, (0, 0), area=pygame.Rect(start_x, 0, w1, sky_h))
                dest.blit(sky, (w1, 0), area=pygame.Rect(0, 0, w2, sky_h))

            # Escalar al alto visible (horizon)
            if dest.get_height() != view_h:
                dest = pygame.transform.scale(dest, (view_w, view_h))
            self.screen.blit(dest, (0, 0))
            return True
        except Exception:
            return False

    def _render_wall_column(self, ray, column_index, horizon):
        """Genera los datos de una columna de pared a partir de un rayo."""
        wall_type = ray.get("wall_type", 0)
        if wall_type == 0:
            return None

        distance = max(ray.get("distance", 0.0), Config.TILE_SIZE * 0.05)
        proj_height = int(ray.get("proj_height", (Config.TILE_SIZE * Config.SCREEN_HEIGHT) / distance))

        side = ray.get("side", 0)
        texture_offset = ray.get("texture_offset")

        texture = self.texture_manager.get_texture(wall_type)
        tex_width = texture.get_width()
        tex_height = texture.get_height()

        if texture_offset is None:
            hit_x = ray.get("hit_x", 0)
            hit_y = ray.get("hit_y", 0)
            tex_coord = hit_y if side == 0 else hit_x
            texture_offset = (tex_coord % Config.TILE_SIZE) / Config.TILE_SIZE
        tex_x = int(texture_offset * tex_width)
        tex_x = max(0, min(tex_width - 1, tex_x))

        column_width = self.column_width
        x = int(column_index * self.column_width)

        # Caso 1: pared normal (lejos/media distancia)
        if proj_height < Config.SCREEN_HEIGHT:
            try:
                wall_column = texture.subsurface(tex_x, 0, 1, tex_height)
            except ValueError:
                return None
            try:
                wall_column = pygame.transform.scale(
                    wall_column,
                    (column_width, proj_height)
                )
            except Exception:
                pass
            y = int(horizon - proj_height // 2)
            column_height = proj_height
        else:
            texture_visible_height = tex_height * Config.SCREEN_HEIGHT / proj_height
            texture_visible_height = max(1, int(texture_visible_height))
            tex_y_start = (tex_height / 2) - (texture_visible_height / 2)
            try:
                wall_column = texture.subsurface(
                    tex_x,
                    int(tex_y_start),
                    1,
                    int(texture_visible_height)
                )
            except ValueError:
                try:
                    wall_column = texture.subsurface(tex_x, 0, 1, tex_height)
                except ValueError:
                    return None
            try:
                wall_column = pygame.transform.scale(
                    wall_column,
                    (column_width, Config.SCREEN_HEIGHT)
                )
            except Exception:
                pass
            y = 0
            column_height = Config.SCREEN_HEIGHT

        shade_factor = max(0.2, 1 - (distance / Config.MAX_DEPTH))
        if side == 1:
            shade_factor *= 0.75

        shade_value = max(0, min(255, int(255 * shade_factor)))

        render_item = {
            "type": "wall",
            "distance": distance,
            "wall_type": wall_type,
            "surface": wall_column,
            "x": x,
            "y": y,
            "height": column_height,
            "shade_value": shade_value,
            "shade_factor": shade_factor,
            "side": side,
            "tex_x": tex_x,
            "rect": (x, y, column_width, column_height),
        }

        try:
            shaded = wall_column.copy()
            shaded.fill(
                (shade_value, shade_value, shade_value, 255),
                special_flags=pygame.BLEND_RGBA_MULT
            )
            shaded = self._apply_vertical_shading(shaded)
            render_item["surface"] = shaded
        except Exception:
            base_color = self.wall_colors.get(wall_type, Config.GRAY)
            color = tuple(int(c * shade_factor) for c in base_color)
            render_item["fallback_color"] = color
            render_item["surface"] = None
        else:
            render_item["fallback_color"] = tuple(
                int(c * shade_factor) for c in self.wall_colors.get(wall_type, Config.GRAY)
            )

        return render_item

    def _draw_render_item(self, item):
        item_type = item.get("type")
        if item_type == "wall":
            x = int(item.get("x", 0))
            y = int(item.get("y", 0))
            rect = item.get("rect", (x, y, self.column_width + 1, item.get("height", 0)))
            surface = item.get("surface")
            if surface is not None:
                try:
                    self.screen.blit(surface, (x, y))
                    return
                except Exception:
                    pass
            color = item.get("fallback_color") or self.wall_colors.get(item.get("wall_type"), Config.GRAY)
            try:
                rx, ry, rw, rh = rect
                pygame.draw.rect(self.screen, color, (int(rx), int(ry), int(rw), int(rh)))
            except Exception:
                pass
        elif item_type == "spell":
            try:
                pygame.draw.circle(
                    self.screen,
                    item.get("color", Config.YELLOW),
                    (int(item.get("x", 0)), int(item.get("y", 0))),
                    max(1, int(item.get("radius", 3))),
                )
            except Exception:
                pass

    def _gather_spell_commands(self, player, spells, horizon, rays):
        commands = []
        if not spells or not rays:
            return commands

        for s in spells:
            try:
                dx = s.x - player.x
                dy = s.y - player.y
                distance = max(1.0, (dx * dx + dy * dy) ** 0.5)

                angle_to = math.atan2(dy, dx)
                angle_diff = (angle_to - player.angle + math.pi) % (2 * math.pi) - math.pi
                if abs(angle_diff) > Config.HALF_FOV:
                    continue

                ray_index_f = (angle_diff + Config.HALF_FOV) / Config.DELTA_ANGLE
                ray_index = int(max(0, min(Config.NUM_RAYS - 1, ray_index_f)))

                wall_dist = rays[ray_index].get("distance", 0)
                if distance > wall_dist:
                    continue

                sprite_h = (Config.TILE_SIZE * Config.SCREEN_HEIGHT) / distance
                radius = int(max(3, sprite_h * 0.15))

                screen_x = int((ray_index_f / Config.NUM_RAYS) * Config.SCREEN_WIDTH)
                screen_y = horizon

                commands.append({
                    "type": "spell",
                    "distance": distance,
                    "x": screen_x,
                    "y": screen_y,
                    "radius": radius,
                    "color": getattr(s, 'color', (255, 200, 50)),
                })
            except Exception:
                continue
        return commands

    def render_crosshair(self, size: int = 3, color=Config.WHITE):
        """Dibuja un punto de mira simple en el centro de la pantalla."""
        cx = Config.SCREEN_WIDTH // 2
        cy = Config.SCREEN_HEIGHT // 2
        try:
            pygame.draw.circle(self.screen, color, (cx, cy), max(1, int(size)))
        except Exception:
            pass

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
