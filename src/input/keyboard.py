"""
Manejador de input de teclado y mouse
Controla el movimiento del jugador
"""
import pygame
from src.game.config import Config

class KeyboardHandler:
    def __init__(self):
        self.mouse_sensitivity = 0.001  # Sensibilidad reducida (solo X)
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        
    def update(self, player, dt):
        """
        Actualiza el input del jugador
        dt: delta time en segundos
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

        # Sprint con Shift
        speed = player.move_speed
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            speed *= getattr(Config, "PLAYER_SPRINT_MULT", 1.5)

        # Aplicar movimiento (CORREGIDO: ahora pasa dt correctamente)
        if forward != 0 or strafe != 0:
            player.move(forward, strafe, dt, speed=speed)

        # Rotación con flechas (alternativa al mouse)
        if keys[pygame.K_LEFT]:
            player.rotate(-1, dt)
        if keys[pygame.K_RIGHT]:
            player.rotate(1, dt)

        # Pausa con P
        if keys[pygame.K_p]:
            # Toggle en engine mediante estado; aquí solo se señala
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"action": "toggle_pause"}))

        # Mouse para rotación (CORREGIDO: ahora funciona correctamente)
        if pygame.event.get_grab():  # Solo si el mouse está capturado
            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            if mouse_dx != 0:
                player.rotate(mouse_dx * self.mouse_sensitivity, dt)

    def release_mouse(self):
        """Libera el mouse (para menús)"""
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # Limpiar el buffer de movimiento del mouse
        pygame.mouse.get_rel()
    
    def capture_mouse(self):
        """Captura el mouse (para jugar)"""
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        # Limpiar el buffer de movimiento del mouse
        pygame.mouse.get_rel()
