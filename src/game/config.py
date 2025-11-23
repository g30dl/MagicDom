"""
Configuración global del juego
Contiene todas las constantes y configuraciones
"""
import math

class Config:
    # Configuración de pantalla
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 70
    
    # Configuración de raycasting
    FOV = math.pi / 3  # 60 grados
    HALF_FOV = FOV / 2
    # Resolución adaptativa: más ancho => más rayos, limitado por BASE_NUM_RAYS
    BASE_NUM_RAYS = 160
    NUM_RAYS = max(BASE_NUM_RAYS, int(SCREEN_WIDTH / 4))
    MAX_DEPTH = 800  # Distancia máxima de visión
    DELTA_ANGLE = FOV / NUM_RAYS
    # Factor de shearing vertical para mirar arriba/abajo (pitch)
    PITCH_SHEAR_FACTOR = 0.15

    # Texturas de paredes
    TEXTURE_SIZE = 256
    WALL_TEXTURES_PATH = "assets/textures"  # pared1.png vive aqui actualmente
    WALL_TEXTURE_MAP = {
        1: "pared1.png",
        # Otros tipos pueden agregarse luego; caeran en placeholder si falta archivo
        2: "madera_oscura.png",
        3: "magica_azul.png",
        4: "destructible_oro.png",
    }
    
    # Tamaño del mapa
    TILE_SIZE = 128
    
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
    
    # Jugador (AJUSTADO: velocidades más apropiadas)
    PLAYER_SPEED = 1.5  # Velocidad de movimiento (era 2)
    PLAYER_ROT_SPEED = 0.04  # Velocidad de rotación (era 0.05)
    PLAYER_SIZE = 10

    # Spawn del jugador
    # Usar un tile específico (col, row). Si es None, se elegirá automáticamente
    SPAWN_TILE = None  # ejemplo: (1, 1)
    
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

    # HUD de manos (escala y posicionamiento)
    # - HEIGHT_RATIO: fracción del alto de pantalla usada para el sprite
    # - MAX_WIDTH_RATIO: fracción del ancho máximo permitido (clamp)
    # - BOTTOM_OFFSET: píxeles desde el borde inferior; negativo permite que se salga por abajo
    # - CENTER_OFFSET_X: desplazamiento horizontal (izquierda/ derecha)
    HUD_HANDS_HEIGHT_RATIO = 0.85
    HUD_HANDS_MAX_WIDTH_RATIO = 0.98
    HUD_HANDS_BOTTOM_OFFSET = -40
    HUD_HANDS_CENTER_OFFSET_X = 0
    # Anclaje horizontal: 'center' | 'right' | 'left'
    HUD_HANDS_ANCHOR = 'right'
    # Si HUD_HANDS_ANCHOR = 'right', overflow positivo hace que se salga por la derecha
    HUD_HANDS_RIGHT_OVERFLOW = 120
    # Si HUD_HANDS_ANCHOR = 'left', offset desde el borde izquierdo (puede ser negativo)
    HUD_HANDS_LEFT_OFFSET = 0
