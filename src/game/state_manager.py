"""
Gestor de estados del juego
Maneja las transiciones entre diferentes estados (menú, jugando, pausa, etc.)
"""
from enum import Enum

# Estados del juego
class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SETTINGS = "settings"
    GAME_OVER = "game_over"
    VICTORY = "victory"

# Gestor de estados
class StateManager:
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
    
    def change_state(self, new_state: GameState):
        # Cambia al nuevo estado
        self.previous_state = self.current_state
        self.current_state = new_state
        print(f"Estado cambiado: {self.previous_state.value} -> {self.current_state.value}")
    
    def get_state(self) -> GameState:
        # Retorna el estado actual
        return self.current_state
    
    def get_previous_state(self) -> GameState:
        # Retorna el estado anterior
        return self.previous_state
    
    def is_playing(self) -> bool:
        # Verifica si el juego está en modo jugando
        return self.current_state == GameState.PLAYING