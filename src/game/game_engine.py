"""
Motor principal del juego
Maneja el loop principal y coordina todos los sistemas
"""
import pygame
from .state_manager import StateManager, GameState
from .config import Config
from src.rendering.renderer import Renderer
from src.entities.player import Player
from src.input.keyboard import KeyboardHandler

class GameEngine:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicializar sistemas
        self.state_manager = StateManager()
        self.renderer = Renderer(screen)
        self.keyboard_handler = KeyboardHandler()
        
        # Inicializar jugador en el centro del mapa
        self.player = Player(x=300, y=300, angle=0)
        
        # Pasar el mapa al jugador para colisiones
        from src.rendering.raycaster import EXAMPLE_MAP
        self.player.set_map(EXAMPLE_MAP)
        
        # Font para UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

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
            
            # Renderizar
            self.render(current_state)
            
            pygame.display.flip()
    
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
    
    def update_pause(self):
        """Actualiza lógica de pausa"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.state_manager.change_state(GameState.PLAYING)
            self.keyboard_handler.capture_mouse()
        if keys[pygame.K_m]:
            self.state_manager.change_state(GameState.MENU)
            self.keyboard_handler.release_mouse()
    
    def render(self, state):
        """Renderiza el frame actual"""
        self.screen.fill(Config.BLACK)
        
        if state == GameState.MENU:
            self.render_menu()
        elif state == GameState.PLAYING:
            self.render_game()
        elif state == GameState.PAUSED:
            self.render_pause()
    
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
        self.renderer.render_3d_view(self.player)
        
        # Renderizar minimap (útil para debug)
        self.renderer.render_minimap(self.player, position=(10, 10), scale=5)
        
        # Renderizar HUD simple
        health_text = self.small_font.render(
            f"Salud: {self.player.health}/{self.player.max_health}", 
            True, Config.GREEN
        )
        position_text = self.small_font.render(
            f"Pos: ({int(self.player.x)}, {int(self.player.y)})", 
            True, Config.WHITE
        )
        map_pos = self.player.get_map_position()
        tile_text = self.small_font.render(
            f"Tile: ({map_pos[0]}, {map_pos[1]})", 
            True, Config.WHITE
        )
        angle_text = self.small_font.render(
            f"Ángulo: {int(math.degrees(self.player.angle))}°", 
            True, Config.WHITE
        )
        controls_text = self.small_font.render(
            "WASD: Mover | Mouse: Mirar | ESC: Pausa", 
            True, Config.GRAY
        )
        
        self.screen.blit(health_text, (Config.SCREEN_WIDTH - 250, 10))
        self.screen.blit(position_text, (Config.SCREEN_WIDTH - 250, 40))
        self.screen.blit(tile_text, (Config.SCREEN_WIDTH - 250, 70))
        self.screen.blit(angle_text, (Config.SCREEN_WIDTH - 250, 100))
        self.screen.blit(controls_text, (10, Config.SCREEN_HEIGHT - 30))
    
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