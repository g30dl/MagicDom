"""
Entidad Player completa con movimiento y colisiones.
"""
import math
from src.game.config import Config

class Player:
    def __init__(self, x=300, y=300, angle=0.0, health=100):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.health = int(health)
        self.max_health = int(health)
        
        # Velocidad de movimiento y rotación
        self.move_speed = Config.PLAYER_SPEED
        self.rot_speed = Config.PLAYER_ROT_SPEED
        
        # Radio de colisión del jugador
        self.collision_radius = 20
        
        # Referencia al mapa (se establecerá desde el game engine)
        self.game_map = None
        
        # Pitch para mirar arriba/abajo (opcional para futuro)
        self.pitch = 0.0
    
    def set_map(self, game_map):
        """Establece la referencia al mapa para colisiones"""
        self.game_map = game_map
    
    def check_collision(self, x, y):
        """
        Verifica si la posición (x, y) colisiona con una pared.
        Retorna True si hay colisión, False si es espacio libre.
        """
        if self.game_map is None:
            return False
        
        # Convertir posición a coordenadas del mapa
        map_x = int(x // Config.TILE_SIZE)
        map_y = int(y // Config.TILE_SIZE)
        
        # Verificar límites del mapa
        if map_y < 0 or map_y >= len(self.game_map):
            return True
        if map_x < 0 or map_x >= len(self.game_map[0]):
            return True
        
        # Verificar si hay pared
        return self.game_map[map_y][map_x] != 0
    
    def check_collision_circle(self, x, y):
        """
        Verifica colisión usando el radio del jugador.
        Chequea múltiples puntos alrededor del círculo de colisión.
        """
        # Puntos cardinales alrededor del jugador
        check_points = [
            (x + self.collision_radius, y),  # Derecha
            (x - self.collision_radius, y),  # Izquierda
            (x, y + self.collision_radius),  # Abajo
            (x, y - self.collision_radius),  # Arriba
            (x + self.collision_radius * 0.7, y + self.collision_radius * 0.7),  # Diagonal
            (x - self.collision_radius * 0.7, y + self.collision_radius * 0.7),
            (x + self.collision_radius * 0.7, y - self.collision_radius * 0.7),
            (x - self.collision_radius * 0.7, y - self.collision_radius * 0.7),
        ]
        
        # Si cualquier punto colisiona, hay colisión
        for px, py in check_points:
            if self.check_collision(px, py):
                return True
        
        return False
    
    def move(self, forward: float, strafe: float, dt: float, speed: float = None):
        """
        Mueve al jugador usando movimiento relativo a su ángulo con colisiones.
        forward: 1 adelante, -1 atrás
        strafe: 1 derecha, -1 izquierda
        dt: delta time en segundos
        """
        if speed is None:
            speed = self.move_speed
        
        # Calcular desplazamiento (CORREGIDO: multiplicador ajustado)
        move_x = (math.cos(self.angle) * forward - math.sin(self.angle) * strafe) * speed * dt * 100
        move_y = (math.sin(self.angle) * forward + math.cos(self.angle) * strafe) * speed * dt * 100
        
        # Nueva posición propuesta
        new_x = self.x + move_x
        new_y = self.y + move_y
        
        # Sistema de colisión por ejes (sliding)
        # Intentar mover en X
        if not self.check_collision_circle(new_x, self.y):
            self.x = new_x
        
        # Intentar mover en Y
        if not self.check_collision_circle(self.x, new_y):
            self.y = new_y
    
    def rotate(self, delta: float, dt: float, rot_speed: float = None):
        """
        Rota al jugador.
        delta: cantidad de rotación (puede ser teclas o mouse)
        dt: delta time en segundos
        """
        if rot_speed is None:
            rot_speed = self.rot_speed
        
        # Aplicar rotación (CORREGIDO: multiplicador ajustado)
        self.angle += delta * rot_speed * 100
        
        # Normalizar ángulo entre 0 y 2π
        self.angle = self.angle % (2 * math.pi)
    
    def look_up_down(self, delta: float, dt: float):
        """
        Controla el pitch (mirar arriba/abajo).
        Limitado para evitar gimbal lock.
        """
        self.pitch += delta * 50  # CORREGIDO: añadido multiplicador
        # Limitar pitch entre -π/3 y π/3 (aprox -60° a 60°)
        max_pitch = math.pi / 3
        self.pitch = max(-max_pitch, min(max_pitch, self.pitch))
    
    def take_damage(self, damage: int):
        """Recibe daño"""
        self.health -= int(damage)
        if self.health < 0:
            self.health = 0
        print(f"Jugador recibe {damage} de daño. Salud: {self.health}/{self.max_health}")
    
    def heal(self, amount: int):
        """Recupera salud"""
        self.health += int(amount)
        if self.health > self.max_health:
            self.health = self.max_health
    
    def is_alive(self) -> bool:
        """Verifica si el jugador está vivo"""
        return self.health > 0
    
    def update(self, dt: float):
        """
        Actualiza el estado del jugador cada frame.
        Por ahora solo es un placeholder, pero aquí podrías:
        - Aplicar física
        - Regenerar salud
        - Actualizar efectos
        - etc.
        """
        pass
    
    def get_position(self):
        """Retorna la posición actual"""
        return (self.x, self.y)
    
    def get_direction(self):
        """Retorna el vector de dirección del jugador"""
        return (math.cos(self.angle), math.sin(self.angle))
    
    def get_map_position(self):
        """Retorna la posición en el mapa (tile coordinates)"""
        return (int(self.x // Config.TILE_SIZE), int(self.y // Config.TILE_SIZE))