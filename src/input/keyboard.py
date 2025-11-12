"""
Manejador de input de teclado y mouse
Controla el movimiento del jugador
"""
import pygame
from src.game.config import Config

class KeyboardHandler:
    def __init__(self):
        self.mouse_sensitivity = 0.002
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(True)
        
    def update(self, player, dt):
        """
        Actualiza el input del jugador
        """
        # Teclado
        print("checkpoint 6")
        keys = pygame.key.get_pressed()
        print("checkpoint 7")
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
        print("checkpoint 3")
        player.move(forward, strafe, dt)
        print("checkpoint 4")
        # Rotación con flechas (alternativa al mouse)
        if keys[pygame.K_LEFT]:
            player.rotate(-1, dt)
        if keys[pygame.K_RIGHT]:
            player.rotate(1, dt)
        print("checkpoint 2")
        # Mouse para rotación
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        if mouse_dx != 0:
            player.rotate(mouse_dx * self.mouse_sensitivity, dt)
        if mouse_dy != 0:
            player.look_up_down(-mouse_dy * self.mouse_sensitivity, dt)
        print("checkpoint 1")
    
    def release_mouse(self):
        """Libera el mouse (para menús)"""
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
    
    def capture_mouse(self):
        """Captura el mouse (para jugar)"""
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)