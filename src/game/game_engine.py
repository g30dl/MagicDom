"""
Motor principal del juego
Maneja el loop principal y coordina todos los sistemas
"""
import pygame
from .state_manager import StateManager, GameState
from .config import Config
from src.rendering.renderer import Renderer
from src.entities.player import Player
from src.input.voice_handler import VoiceHandler
from src.input.keyboard import KeyboardHandler
from src.audio.sound_manager import SoundManager

class GameEngine:
    def __init__(self, screen):
        
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        
        # Inicializar sistemas
        self.state_manager = StateManager()
        self.renderer = Renderer(screen)
        # self.sound_manager = SoundManager()
        self.keyboard_handler = KeyboardHandler()
         #self.voice_handler = VoiceHandler()
        
        # Inicializar jugador
        
        self.player = Player(x=300, y=300)
        
        # Fase actual
        self.current_phase = 1
        self.targets_destroyed = 0
        
        # Font para UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        

    def run(self):
        """Loop principal del juego"""
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000.0
            print("principal update game")
            # Manejar eventos
            self.handle_events()
            
            # Actualizar según estado
            current_state = self.state_manager.get_state()
            
            if current_state == GameState.MENU:
                self.update_menu()
            elif current_state == GameState.PLAYING:
                print("principal update game")
                self.update_game(dt)
            elif current_state == GameState.PAUSED:
                self.update_pause()
            elif current_state == GameState.SETTINGS:
                self.update_settings()
            
            
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
                        self.sound_manager.pause_music()
                    elif current_state == GameState.PAUSED:
                        self.state_manager.change_state(GameState.PLAYING)
                        self.sound_manager.resume_music()
                    elif current_state == GameState.MENU:
                        self.running = False
                
                # Tecla V para activar reconocimiento de voz
                if event.key == pygame.K_v and self.state_manager.get_state() == GameState.PLAYING:
                    self.handle_voice_command()
    
    def update_menu(self):
        """Actualiza lógica del menú"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.state_manager.change_state(GameState.PLAYING)
            self.sound_manager.play_music("background")
        if keys[pygame.K_s]:
            self.state_manager.change_state(GameState.SETTINGS)
    
    def update_game(self, dt):
        """Actualiza lógica del juego"""
        # Actualizar jugador con input de teclado/mouse
        print("principal update game")
        self.keyboard_handler.update(self.player, dt)
        print("checkpoint 1")
        # Aquí irá la lógica de enemigos, colisiones, etc.
        self.player.update(dt)
        print("checkpoint 2")
    
    def update_pause(self):
        """Actualiza lógica de pausa"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.state_manager.change_state(GameState.PLAYING)
            self.sound_manager.resume_music()
        if keys[pygame.K_m]:
            self.state_manager.change_state(GameState.MENU)
            self.sound_manager.stop_music()
    
    def update_settings(self):
        """Actualiza lógica de configuración"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_BACKSPACE]:
            self.state_manager.change_state(GameState.MENU)
    
    def handle_voice_command(self):
        """Maneja el reconocimiento de voz para hechizos"""
        print("Escuchando comando de voz...")
        spell = self.voice_handler.listen_for_spell()
        
        if spell:
            print(f"Hechizo reconocido: {spell}")
            self.cast_spell(spell)
        else:
            print("No se reconoció ningún hechizo")
    
    def cast_spell(self, spell_name):
        """Lanza un hechizo"""
        current_phase = Config.PHASES[self.current_phase]
        
        if current_phase["required_spell"] and spell_name != current_phase["required_spell"]:
            print(f"Debes usar {current_phase['required_spell']} en esta fase!")
            self.sound_manager.play_sfx("error")
            return
        
        # Lanzar hechizo
        self.player.cast_spell(spell_name)
        self.sound_manager.play_sfx(spell_name)
        
        # Incrementar objetivos destruidos (esto se debe integrar con sistema de enemigos)
        self.targets_destroyed += 1
        
        if self.targets_destroyed >= current_phase["targets"]:
            self.advance_phase()
    
    def advance_phase(self):
        """Avanza a la siguiente fase"""
        self.current_phase += 1
        self.targets_destroyed = 0
        
        if self.current_phase > len(Config.PHASES):
            print("¡Juego completado!")
            self.state_manager.change_state(GameState.MENU)
        else:
            print(f"Fase {self.current_phase}: {Config.PHASES[self.current_phase]['name']}")
    
    def render(self, state):
        """Renderiza el frame actual"""
        self.screen.fill(Config.BLACK)
        
        if state == GameState.MENU:
            self.render_menu()
        elif state == GameState.PLAYING:
            self.render_game()
        elif state == GameState.PAUSED:
            self.render_pause()
        elif state == GameState.SETTINGS:
            self.render_settings()
    
    def render_menu(self):
        """Renderiza el menú principal"""
        title = self.font.render("MAGE ARENA 3D", True, Config.YELLOW)
        start = self.small_font.render("Presiona ENTER para jugar", True, Config.WHITE)
        settings = self.small_font.render("Presiona S para configuración", True, Config.WHITE)
        quit_text = self.small_font.render("Presiona ESC para salir", True, Config.WHITE)
        
        self.screen.blit(title, (Config.SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        self.screen.blit(start, (Config.SCREEN_WIDTH // 2 - start.get_width() // 2, 350))
        self.screen.blit(settings, (Config.SCREEN_WIDTH // 2 - settings.get_width() // 2, 400))
        self.screen.blit(quit_text, (Config.SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 450))
    
    def render_game(self):
        """Renderiza el juego"""
        # Renderizar vista 3D
        self.renderer.render_3d_view(self.player)
        
        # Renderizar HUD
        phase_info = Config.PHASES[self.current_phase]
        phase_text = self.small_font.render(
            f"Fase {self.current_phase}: {phase_info['name']}", 
            True, Config.YELLOW
        )
        objective_text = self.small_font.render(
            phase_info['objective'], 
            True, Config.WHITE
        )
        progress_text = self.small_font.render(
            f"Progreso: {self.targets_destroyed}/{phase_info['targets']}", 
            True, Config.GREEN
        )
        voice_text = self.small_font.render(
            "Presiona V para comando de voz", 
            True, Config.GRAY
        )
        
        self.screen.blit(phase_text, (10, 10))
        self.screen.blit(objective_text, (10, 40))
        self.screen.blit(progress_text, (10, 70))
        self.screen.blit(voice_text, (10, Config.SCREEN_HEIGHT - 30))
    
    def render_pause(self):
        """Renderiza menú de pausa"""
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
    
    def render_settings(self):
        """Renderiza menú de configuración"""
        title = self.font.render("CONFIGURACIÓN", True, Config.YELLOW)
        music_vol = self.small_font.render(f"Volumen Música: {int(Config.MUSIC_VOLUME * 100)}%", True, Config.WHITE)
        sfx_vol = self.small_font.render(f"Volumen Efectos: {int(Config.SFX_VOLUME * 100)}%", True, Config.WHITE)
        back = self.small_font.render("BACKSPACE - Volver", True, Config.GRAY)
        
        self.screen.blit(title, (Config.SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        self.screen.blit(music_vol, (Config.SCREEN_WIDTH // 2 - music_vol.get_width() // 2, 300))
        self.screen.blit(sfx_vol, (Config.SCREEN_WIDTH // 2 - sfx_vol.get_width() // 2, 350))
        self.screen.blit(back, (Config.SCREEN_WIDTH // 2 - back.get_width() // 2, 450))