"""
Entidad Player con movimiento y colisiones en 2D (sin pitch).
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
        # Bosteos temporales
        self.speed_boost_multiplier = 1.0
        self.speed_boost_timer = 0.0

        # Radio de colisión del jugador
        self.collision_radius = 20

        # Referencia al mapa (se establecerá desde el game engine)
        self.game_map = None

    def set_map(self, game_map):
        """Establece la referencia al mapa para colisiones."""
        self.game_map = game_map

    def check_collision(self, x, y):
        """
        Verifica si la posición (x, y) colisiona con una pared.
        Retorna True si hay colisión, False si es espacio libre.
        """
        if self.game_map is None:
            return False

        map_x = int(x // Config.TILE_SIZE)
        map_y = int(y // Config.TILE_SIZE)

        if map_y < 0 or map_y >= len(self.game_map):
            return True
        if map_x < 0 or map_x >= len(self.game_map[0]):
            return True

        return self.game_map[map_y][map_x] != 0

    def check_collision_circle(self, x, y):
        """
        Verifica colisión usando el radio del jugador con quick-rejection
        y 4 puntos cardinales (menos coste que 8 puntos).
        """
        # Tile central bloqueado => colisión directa
        if self.check_collision(x, y):
            return True

        r = self.collision_radius
        check_points = (
            (x + r, y),
            (x - r, y),
            (x, y + r),
            (x, y - r),
        )

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
        speed *= getattr(self, "speed_boost_multiplier", 1.0)

        move_x = (math.cos(self.angle) * forward - math.sin(self.angle) * strafe) * speed * dt * 100
        move_y = (math.sin(self.angle) * forward + math.cos(self.angle) * strafe) * speed * dt * 100

        new_x = self.x + move_x
        new_y = self.y + move_y

        if not self.check_collision_circle(new_x, self.y):
            self.x = new_x

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

        self.angle += delta * rot_speed * 100
        self.angle = self.angle % (2 * math.pi)

    def take_damage(self, damage: int):
        """Recibe daño."""
        dmg = int(damage)
        self.health -= dmg
        if self.health < 0:
            self.health = 0
        try:
            callback = getattr(self, "on_hit_callback", None)
            if callback:
                callback(dmg)
        except Exception:
            pass
        print(f"Jugador recibe {dmg} de daño. Salud: {self.health}/{self.max_health}")

    def heal(self, amount: int):
        """Recupera salud."""
        self.health = min(self.max_health, self.health + int(amount))

    def is_alive(self) -> bool:
        """Verifica si el jugador está vivo."""
        return self.health > 0

    def update(self, dt: float):
        """Actualiza el estado del jugador cada frame (timers)."""
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            if self.speed_boost_timer <= 0:
                self.speed_boost_timer = 0
                self.speed_boost_multiplier = 1.0

    def apply_speed_boost(self, multiplier: float, duration: float):
        """Aplica un boost de velocidad temporal."""
        self.speed_boost_multiplier = max(1.0, float(multiplier))
        self.speed_boost_timer = max(0.0, float(duration))

    def get_position(self):
        """Retorna la posición actual."""
        return (self.x, self.y)

    def get_direction(self):
        """Retorna el vector de dirección del jugador."""
        return (math.cos(self.angle), math.sin(self.angle))

    def get_map_position(self):
        """Retorna la posición en el mapa (tile coordinates)."""
        return (int(self.x // Config.TILE_SIZE), int(self.y // Config.TILE_SIZE))
