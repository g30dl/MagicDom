"""
Manejador de input de teclado y mouse
Controla el movimiento del jugador
"""
import pygame
from src.game.config import Config

class KeyboardHandler:
    def __init__(self):
        self.mouse_sensitivity = 0.02
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
    def update(self, player, dt):
        """
        Actualiza el input del jugador
        """
        # Teclado
        keys = pygame.key.get_pressed()
        
        # Movimiento WASD
        forward = 0
        strafe = 0
        
        if keys[pygame.K_w]:
            forward = 1
        if keys[pygame.K_s]:
            forward = -1
        if keys[pygame.K_a]:
            strafe = -1
        if keys[pygame.K_d]:
            strafe = 1
        
        # Aplicar movimiento
        if forward != 0 or strafe != 0:
            player.move(forward, strafe, dt)
        
        # Rotación con flechas (alternativa al mouse)
        if keys[pygame.K_LEFT]:
            player.rotate(-1, dt)
        if keys[pygame.K_RIGHT]:
            player.rotate(1, dt)
        
        # Mouse para rotación
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        if mouse_dx != 0:
            player.rotate(mouse_dx * self.mouse_sensitivity, dt)
        if mouse_dy != 0:
            player.look_up_down(-mouse_dy * self.mouse_sensitivity, dt)
    
    def release_mouse(self):
        """Libera el mouse (para menús)"""
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
    
    def capture_mouse(self):
        """Captura el mouse (para jugar)"""
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)