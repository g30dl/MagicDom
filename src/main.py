"""
Mage Arena 3D - Juego de combate mágico con control por voz
Punto de entrada principal del juego
"""
import pygame
import sys
from src.game import GameEngine, Config

def main():
    """Inicializa y ejecuta el juego"""
    pygame.init()
   
    pygame.mixer.init()
    
    
    # Configurar pantalla
    screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pygame.display.set_caption("MageDoom Voice")
    
    # Crear instancia del juego
    game = GameEngine(screen)
    
    try:
        
        game.run()
        
    except KeyboardInterrupt:
        print("\nJuego interrumpido por el usuario")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()