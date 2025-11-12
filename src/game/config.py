"""
Configuración global del juego
Contiene todas las constantes y configuraciones
"""
import math

class Config:
    # Configuración de pantalla
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    
    # Configuración de raycasting
    FOV = math.pi / 3  # 60 grados
    HALF_FOV = FOV / 2
    NUM_RAYS = 120  # Cantidad de rayos (más = mejor calidad)
    MAX_DEPTH = 800  # Distancia máxima de visión
    DELTA_ANGLE = FOV / NUM_RAYS
    
    # Tamaño del mapa
    TILE_SIZE = 64
    
    # Colores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GRAY = (100, 100, 100)
    DARK_GRAY = (50, 50, 50)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    
    # Jugador
    PLAYER_SPEED = 2
    PLAYER_ROT_SPEED = 0.05
    PLAYER_SIZE = 10
    
    # Configuración de voz
    VOICE_LANGUAGE = "es-ES"  # Español
    VOICE_TIMEOUT = 3  # Segundos de espera
    
    # Hechizos disponibles
    SPELLS = {
        "bola de fuego": "fireball",
        "fuego": "fireball",
        "rayo": "lightning",
        "trueno": "lightning",
        "relámpago": "lightning"
    }
    
    # Fases del juego
    PHASES = {
        1: {
            "name": "Destrucción",
            "objective": "Destruye el objetivo con bola de fuego",
            "required_spell": "fireball",
            "targets": 3
        },
        2: {
            "name": "Cacería",
            "objective": "Elimina a los enemigos con rayo",
            "required_spell": "lightning",
            "targets": 5
        },
        3: {
            "name": "Desafío Final",
            "objective": "Derrota al jefe usando todos tus hechizos",
            "required_spell": None,
            "targets": 1
        }
    }
    
    # Configuración de audio
    MUSIC_VOLUME = 0.3
    SFX_VOLUME = 0.7