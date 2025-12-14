"""
Motor principal del juego
Maneja el loop principal y coordina todos los sistemas
"""
import pygame
import math
import random
import threading
import os
from collections import deque
from .state_manager import StateManager, GameState
from .config import Config
from src.rendering.renderer import Renderer
from src.entities.player import Player
from src.input.keyboard import KeyboardHandler
from src.input.voice_handler import VoiceHandler
from src.entities.spells import SpellManager
from src.entities.particles import ParticleManager
from src.entities.enemies.enemy import EnemyManager
from src.audio.sound_manager import SoundManager
from src.rendering.hud_hands import HUDHands


class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.restart_requested = False

        # Inicializar sistemas
        self.state_manager = StateManager()
        from src.rendering.map_manager import MapManager
        self.map_manager = MapManager()
        game_map = self.map_manager.get_map()
        self.enemy_spawns = getattr(self.map_manager, "enemy_spawns", [])
        self.renderer = Renderer(screen, self.map_manager)
        self.keyboard_handler = KeyboardHandler()
        self.sound_manager = self._init_sound_manager()
        self.blood_surface = self._load_blood_overlay()
        self.blood_timer = 0.0
        self.blood_duration = 0.7
        # Overlay de curación y carteles
        self.heal_flash_timer = 0.0
        self.heal_flash_duration = 0.5
        self.sign_message = None
        self.sign_alpha = 0.0
        self.sign_target_alpha = 0.0
        # Overlay de curación (flash verde al sanar)
        self.heal_flash_timer = 0.0
        self.heal_flash_duration = 0.5

        # Reconocimiento de voz (estado y buffer)
        self.voice_handler = None
        self._voice_lock = threading.Lock()
        self.recognized_words = deque(maxlen=10)
        self._voice_error = None

        # Cargar mapa y generar un punto de spawn seguro (centro de un tile libre)
        tile = getattr(Config, "SPAWN_TILE", None)
        spawn_x = spawn_y = None
        if tile is not None and isinstance(tile, tuple) and len(tile) == 2:
            col, row = int(tile[0]), int(tile[1])
            if 0 <= row < len(game_map) and 0 <= col < len(game_map[0]) and game_map[row][col] == 0:
                spawn_x = col * Config.TILE_SIZE + Config.TILE_SIZE // 2
                spawn_y = row * Config.TILE_SIZE + Config.TILE_SIZE // 2
        if spawn_x is None:
            spawn_x, spawn_y = self._find_spawn_center(game_map)
        self.player = Player(x=spawn_x, y=spawn_y, angle=0)
        # Pasar el mapa al jugador para colisiones
        self.player.set_map(game_map)
        self.player.on_hit_callback = self._on_player_hit

        # Enemigos y mapa para IA
        self.enemy_manager = EnemyManager(game_map)

        # Font para UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.health_font = pygame.font.Font(None, 54)

        # Iniciar escucha continua de voz (si es posible)
        try:
            self.voice_handler = VoiceHandler()
            self.voice_handler.start_continuous_listening(self._on_voice_text)
        except Exception as e:
            # Guardar el error para mostrar en HUD
            self.voice_handler = None
            self._voice_error = str(e)

        # Sistema de hechizos y partículas
        self.particles = ParticleManager()
        self.spells = SpellManager(
            game_map=self.player.game_map,
            player=self.player,
            particle_manager=self.particles,
            sound_manager=self.sound_manager,
        )

        # Spawns iniciales
        self._spawn_initial_enemies()

    def run(self):
        """Loop principal del juego"""
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0

            # Manejar eventos
            self.handle_events()

            # Actualizar según estado
            current_state = self.state_manager.get_state()

            if current_state == GameState.MENU:
                self.update_menu()
            elif current_state == GameState.PLAYING:
                self.update_game(dt)
            elif current_state == GameState.PAUSED:
                self.update_pause()
            elif current_state == GameState.GAME_OVER:
                self.update_game_over()

            # Renderizar
            self.render(current_state)

            pygame.display.flip()

        # Al salir, detener hilo de voz si está activo
        if self.voice_handler is not None:
            try:
                self.voice_handler.stop()
            except Exception:
                pass

    def handle_events(self):
        """Maneja los eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Manejo de estados con ESC
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    current_state = self.state_manager.get_state()
                    if current_state == GameState.PLAYING:
                        self.state_manager.change_state(GameState.PAUSED)
                        self.keyboard_handler.release_mouse()
                    elif current_state == GameState.PAUSED:
                        self.state_manager.change_state(GameState.PLAYING)
                        self.keyboard_handler.capture_mouse()
                    elif current_state == GameState.MENU:
                        self.running = False

    def update_menu(self):
        """Actualiza lógica del menú"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.state_manager.change_state(GameState.PLAYING)
            self.keyboard_handler.capture_mouse()

    def update_game(self, dt):
        """Actualiza lógica del juego"""
        # Actualizar jugador con input de teclado/mouse
        self.keyboard_handler.update(self.player, dt)

        # Actualizar jugador
        self.player.update(dt)
        if self.blood_timer > 0:
            self.blood_timer -= dt

        # Actualizar enemigos (si hay)
        try:
            self.enemy_manager.update_all(dt, self.player)
            self.enemy_manager.remove_dead()
        except Exception:
            pass

        # Actualizar hechizos y partículas
        try:
            enemies = self.enemy_manager.get_alive_enemies()
            self.spells.update(dt, enemies=enemies)
            self.particles.update(dt)
        except Exception:
            pass

        # Actualizar HUD de manos
        try:
            if not hasattr(self, 'hud_hands') or self.hud_hands is None:
                from src.rendering.hud_hands import HUDHands
                self.hud_hands = HUDHands()
            self.hud_hands.update(dt)
        except Exception:
            pass

        # Overlay de carteles (detección de cercanía)
        self._update_sign_overlay(dt)

        # Check muerte del jugador
        if not self.player.is_alive():
            self.state_manager.change_state(GameState.GAME_OVER)
            self.keyboard_handler.release_mouse()

    def update_pause(self):
        """Actualiza lógica de pausa"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.state_manager.change_state(GameState.PLAYING)
            self.keyboard_handler.capture_mouse()
        if keys[pygame.K_m]:
            self.state_manager.change_state(GameState.MENU)
            self.keyboard_handler.release_mouse()

    def update_game_over(self):
        """Espera input en Game Over."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self._restart_game()
        if keys[pygame.K_ESCAPE]:
            self.running = False

    def render(self, state):
        """Renderiza el frame actual"""
        self.screen.fill(Config.BLACK)

        if state == GameState.MENU:
            self.render_menu()
        elif state == GameState.PLAYING:
            self.render_game()
        elif state == GameState.PAUSED:
            self.render_pause()
        elif state == GameState.GAME_OVER:
            self.render_game_over()

    def render_menu(self):
        """Renderiza el menú principal"""
        title = self.font.render("MAGE ARENA 3D", True, Config.YELLOW)
        start = self.small_font.render("Presiona ENTER para jugar", True, Config.WHITE)
        quit_text = self.small_font.render("Presiona ESC para salir", True, Config.WHITE)

        self.screen.blit(title, (Config.SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        self.screen.blit(start, (Config.SCREEN_WIDTH // 2 - start.get_width() // 2, 350))
        self.screen.blit(quit_text, (Config.SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 400))

    def render_game(self):
        """Renderiza el juego"""
        # Renderizar vista 3D
        active_spells = None
        enemies_to_draw = None
        try:
            active_spells = self.spells.get_active_spells()
        except Exception:
            active_spells = None
        try:
            enemies_to_draw = self.enemy_manager.get_renderable_enemies()
        except Exception:
            enemies_to_draw = None
        self.renderer.render_3d_view(self.player, spells=active_spells, enemies=enemies_to_draw)

        # HUD de manos
        try:
            if hasattr(self, 'hud_hands') and self.hud_hands is not None:
                self.hud_hands.draw(self.screen)
        except Exception:
            pass

        # Punto de mira (dot) en el centro
        try:
            self.renderer.render_crosshair(size=3, color=Config.WHITE)
        except Exception:
            pass

        # Renderizar minimap (útil para debug)
        try:
            self.renderer.render_minimap(
                self.player, position=(10, 10), scale=5,
                spells=self.spells.get_active_spells(),
                particles=self.particles.get_particles(),
            )
        except Exception:
            self.renderer.render_minimap(self.player, position=(10, 10), scale=5)

        # Renderizar HUD simple
        health_text = self.health_font.render(
            f"Salud: {self.player.health}/{self.player.max_health}",
            True, Config.GREEN,
        )
        # Solo mostrar salud en grande
        health_pos = (20, Config.SCREEN_HEIGHT - health_text.get_height() - 20)
        self.screen.blit(health_text, health_pos)

        # Overlay de sangre cuando recibe daño
        self._draw_blood_overlay()
        # Overlay de curación (flash verde)
        self._draw_heal_overlay()
        # Panel de cartel cercano
        self._draw_sign_panel()
        # HUD de boost de velocidad
        self._draw_speed_timer()
        # Panel de cartel cercano
        self._draw_sign_panel()

        # Ocultar chat/estado de voz y otros indicadores no esenciales en pantalla

    def render_pause(self):
        """Renderiza menú de pausa"""
        # Renderizar el juego detrás
        self.renderer.render_3d_view(self.player)

        # Oscurecer fondo
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Config.BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("PAUSA", True, Config.YELLOW)
        resume = self.small_font.render("R - Reanudar", True, Config.WHITE)
        menu = self.small_font.render("M - Menú Principal", True, Config.WHITE)

        self.screen.blit(pause_text, (Config.SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 250))
        self.screen.blit(resume, (Config.SCREEN_WIDTH // 2 - resume.get_width() // 2, 350))
        self.screen.blit(menu, (Config.SCREEN_WIDTH // 2 - menu.get_width() // 2, 400))

    def render_game_over(self):
        """Pantalla de Game Over con opciones."""
        # Mostrar última vista congelada
        self.renderer.render_3d_view(self.player)

        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        title = self.font.render("GAME OVER", True, Config.RED)
        retry = self.small_font.render("R - Reiniciar", True, Config.WHITE)
        quit_text = self.small_font.render("ESC - Salir", True, Config.WHITE)

        self.screen.blit(title, (Config.SCREEN_WIDTH // 2 - title.get_width() // 2, 240))
        self.screen.blit(retry, (Config.SCREEN_WIDTH // 2 - retry.get_width() // 2, 340))
        self.screen.blit(quit_text, (Config.SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 380))

    def _spawn_initial_enemies(self):
        """Spawnea enemigos marcados en el mapa (celda 9). Si no hay, usa fallback alejado."""
        if not self.enemy_manager:
            return

        spawn_tiles = list(self.enemy_spawns or [])
        if not spawn_tiles:
            spawn_tiles = self._pick_enemy_spawn_tiles(count=3, min_distance=Config.TILE_SIZE * 4)

        for col, row in spawn_tiles:
            x = col * Config.TILE_SIZE + Config.TILE_SIZE // 2
            y = row * Config.TILE_SIZE + Config.TILE_SIZE // 2
            try:
                self.enemy_manager.add_enemy(x, y, enemy_type="rockbad")
            except Exception:
                continue

    def _pick_enemy_spawn_tiles(self, count=3, min_distance=Config.TILE_SIZE * 3):
        """Devuelve hasta `count` tiles libres lejos del jugador."""
        game_map = self.player.game_map if hasattr(self.player, "game_map") else None
        if not game_map:
            return []
        rows = len(game_map)
        cols = len(game_map[0]) if rows else 0
        player_tile = self.player.get_map_position()
        min_tiles = max(2, int(min_distance // Config.TILE_SIZE))

        candidates = []
        for row in range(1, max(0, rows - 1)):
            for col in range(1, max(0, cols - 1)):
                if game_map[row][col] != 0:
                    continue
                if abs(col - player_tile[0]) + abs(row - player_tile[1]) < min_tiles:
                    continue
                candidates.append((col, row))

        random.shuffle(candidates)
        return candidates[:count]

    def _load_blood_overlay(self):
        """Carga la textura de sangre en pantalla o un fallback rojo."""
        path = "assets/textures/blood_screen.png"
        try:
            if os.path.exists(path):
                surf = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(surf, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        except Exception:
            pass
        fallback = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        fallback.fill((150, 0, 0, 160))
        return fallback

    def _draw_blood_overlay(self):
        """Dibuja overlay de sangre con fade según el tiempo restante."""
        if self.blood_timer <= 0 or self.blood_surface is None:
            return
        alpha = int(255 * max(0.0, min(1.0, self.blood_timer / self.blood_duration)))
        try:
            overlay = self.blood_surface.copy()
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
        except Exception:
            pass

    def _on_player_hit(self, damage):
        """Se dispara cuando el jugador recibe daño; activa overlay de sangre."""
        self.blood_timer = self.blood_duration

    def _restart_game(self):
        """Reinicia el juego rápidamente re-creando el estado principal."""
        try:
            if self.voice_handler:
                self.voice_handler.stop()
        except Exception:
            pass
        screen = self.screen
        # Re-inicializar todo
        self.__init__(screen)
        self.state_manager.change_state(GameState.PLAYING)
        self.keyboard_handler.capture_mouse()

    def _find_spawn_center(self, game_map):
        """Busca el primer tile libre (valor 0) y retorna su centro en pixeles.
        Evita los bordes para minimizar spawn pegado a paredes.
        """
        height = len(game_map)
        width = len(game_map[0]) if height else 0

        # Buscar dentro del contorno (evitar borde)
        for row in range(1, max(0, height - 1)):
            for col in range(1, max(0, width - 1)):
                if game_map[row][col] == 0:
                    x = col * Config.TILE_SIZE + Config.TILE_SIZE // 2
                    y = row * Config.TILE_SIZE + Config.TILE_SIZE // 2
                    return x, y

        # Fallback: tile (1,1) centrado si no hay libres detectados
        fallback_x = Config.TILE_SIZE + Config.TILE_SIZE // 2
        fallback_y = Config.TILE_SIZE + Config.TILE_SIZE // 2
        return fallback_x, fallback_y

    def _init_sound_manager(self):
        """Crea un SoundManager sin romper el juego si no hay dispositivo."""
        try:
            return SoundManager()
        except Exception as e:
            print(f"[Audio] Desactivado: {e}")
            return None

    # Callback ejecutado por el hilo de voz
    def _on_voice_text(self, text: str):
        parts = [p.strip() for p in text.split() if p.strip()]
        if not parts:
            return
        with self._voice_lock:
            for p in parts:
                self.recognized_words.append(p)
        # Intentar castear el hechizo reconocido (ahora soporta varios comandos)
        try:
            if self.voice_handler:
                spell_name = self.voice_handler.text_to_spell(text.lower())
                if spell_name:
                    spell = self.spells.cast_spell(spell_name)
                    # animación de manos al castear si se lanzó algo
                    if spell:
                        try:
                            if hasattr(self, 'hud_hands') and self.hud_hands is not None:
                                self.hud_hands.trigger_cast()
                        except Exception:
                            pass
                        # Flash verde si es curación
                        if spell_name == "healing":
                            self.heal_flash_timer = self.heal_flash_duration
        except Exception:
            pass

    def _draw_heal_overlay(self):
        """Overlay verdoso corto al curar."""
        if self.heal_flash_timer <= 0:
            return
        alpha = int(180 * max(0.0, min(1.0, self.heal_flash_timer / self.heal_flash_duration)))
        try:
            overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((50, 180, 100, alpha))
            self.screen.blit(overlay, (0, 0))
        except Exception:
            pass
        self.heal_flash_timer -= self.clock.get_time() / 1000.0

    def _update_sign_overlay(self, dt):
        """Calcula si hay un cartel cerca y ajusta el alpha para el fade."""
        message = None
        signs = getattr(self.map_manager, "signs", None)
        if signs:
            px, py = self.player.x, self.player.y
            threshold = Config.TILE_SIZE * 1.2  # radio más corto para no solapar carteles
            for (col, row), msg in signs.items():
                cx = col * Config.TILE_SIZE + Config.TILE_SIZE * 0.5
                cy = row * Config.TILE_SIZE + Config.TILE_SIZE * 0.5
                if math.hypot(cx - px, cy - py) <= threshold:
                    message = msg
                    break

        self.sign_target_alpha = 1.0 if message else 0.0
        fade_speed = 3.5
        if self.sign_target_alpha > self.sign_alpha:
            self.sign_alpha = min(self.sign_target_alpha, self.sign_alpha + dt * fade_speed)
        else:
            self.sign_alpha = max(self.sign_target_alpha, self.sign_alpha - dt * fade_speed)
        self.sign_message = message

    def _draw_sign_panel(self):
        """Dibuja el panel semi-transparente del cartel cercano."""
        if self.sign_alpha <= 0 or not self.sign_message:
            return
        panel_w = min(Config.SCREEN_WIDTH - 80, int(Config.SCREEN_WIDTH * 0.6))
        panel_h = 120
        surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg_alpha = int(170 * self.sign_alpha)
        surf.fill((10, 20, 10, bg_alpha))
        try:
            pygame.draw.rect(surf, (80, 180, 120, min(255, bg_alpha + 50)), surf.get_rect(), 2)
        except Exception:
            pass

        y = 15
        for line in self.sign_message.split("\n"):
            text_surf = self.small_font.render(line, True, Config.WHITE)
            surf.blit(text_surf, (20, y))
            y += text_surf.get_height() + 6

        x = (Config.SCREEN_WIDTH - panel_w) // 2
        y = 40
        self.screen.blit(surf, (x, y))

    def _draw_speed_timer(self):
        """Muestra un cronómetro del boost de velocidad si está activo."""
        timer = getattr(self.player, "speed_boost_timer", 0.0)
        mult = getattr(self.player, "speed_boost_multiplier", 1.0)
        if timer <= 0 or mult <= 1.01:
            return
        text = self.small_font.render(f"Velocidad x{mult:.1f} - {timer:0.1f}s", True, Config.YELLOW)
        pad = 10
        bg = pygame.Surface((text.get_width() + pad * 2, text.get_height() + pad * 2), pygame.SRCALPHA)
        bg.fill((20, 20, 0, 160))
        try:
            pygame.draw.rect(bg, (200, 180, 50, 220), bg.get_rect(), 2)
        except Exception:
            pass
        bg.blit(text, (pad, pad))
        self.screen.blit(bg, (Config.SCREEN_WIDTH - bg.get_width() - 16, Config.SCREEN_HEIGHT - 80))
