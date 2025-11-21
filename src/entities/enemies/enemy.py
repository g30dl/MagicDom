"""
Entidad de enemigo
Base para crear diferentes tipos de enemigos
"""
import math
import random

class Enemy:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.alive = True
        
        # Estadísticas según tipo
        self.stats = {
            "basic": {"health": 50, "damage": 10, "speed": 2},
            "fast": {"health": 30, "damage": 5, "speed": 4},
            "tank": {"health": 100, "damage": 15, "speed": 1},
            "boss": {"health": 200, "damage": 25, "speed": 1.5}
        }
        
        stats = self.stats.get(enemy_type, self.stats["basic"])
        self.health = stats["health"]
        self.max_health = stats["health"]
        self.damage = stats["damage"]
        self.speed = stats["speed"]
        
        # IA
        self.state = "idle"  # idle, chasing, attacking
        self.target = None
        self.attack_cooldown = 0
        self.attack_range = 100
        self.detection_range = 500
    
    def update(self, dt, player):
        """Actualiza el estado del enemigo"""
        if not self.alive:
            return
        
        # Calcular distancia al jugador
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Reducir cooldown de ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Máquina de estados simple
        if distance > self.detection_range:
            self.state = "idle"
            self.idle_behavior(dt)
        elif distance > self.attack_range:
            self.state = "chasing"
            self.chase_player(player, dx, dy, distance, dt)
        else:
            self.state = "attacking"
            self.attack_player(player)
    
    def idle_behavior(self, dt):
        """Comportamiento cuando está inactivo"""
        # Movimiento aleatorio ocasional
        if random.random() < 0.01:
            self.x += random.uniform(-1, 1) * self.speed * dt
            self.y += random.uniform(-1, 1) * self.speed * dt
    
    def chase_player(self, player, dx, dy, distance, dt):
        """Persigue al jugador"""
        # Normalizar dirección
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Moverse hacia el jugador
        self.x += dx * self.speed * dt * 60
        self.y += dy * self.speed * dt * 60
    
    def attack_player(self, player):
        """Ataca al jugador"""
        if self.attack_cooldown <= 0:
            player.take_damage(self.damage)
            self.attack_cooldown = 2.0  # 2 segundos entre ataques
            print(f"¡Enemigo {self.type} ataca! Daño: {self.damage}")
    
    def take_damage(self, damage, damage_type=None):
        """Recibe daño"""
        # Vulnerabilidades/resistencias según tipo de daño
        multiplier = 1.0
        
        if damage_type == "fireball" and self.type == "tank":
            multiplier = 1.5  # Tanques vulnerables al fuego
        elif damage_type == "lightning" and self.type == "fast":
            multiplier = 1.5  # Enemigos rápidos vulnerables al rayo
        
        actual_damage = int(damage * multiplier)
        self.health -= actual_damage
        
        print(f"Enemigo {self.type} recibe {actual_damage} de daño")
        
        if self.health <= 0:
            self.die()
    
    def die(self):
        """Muerte del enemigo"""
        self.alive = False
        self.health = 0
        print(f"¡Enemigo {self.type} eliminado!")
    
    def get_position(self):
        """Retorna la posición actual"""
        return (self.x, self.y)
    
    def get_health_percentage(self):
        """Retorna el porcentaje de salud"""
        return self.health / self.max_health if self.max_health > 0 else 0


class EnemyManager:
    """Administrador de todos los enemigos en el nivel"""
    
    def __init__(self):
        self.enemies = []
    
    def add_enemy(self, x, y, enemy_type="basic"):
        """Agrega un nuevo enemigo"""
        enemy = Enemy(x, y, enemy_type)
        self.enemies.append(enemy)
        return enemy
    
    def update_all(self, dt, player):
        """Actualiza todos los enemigos"""
        for enemy in self.enemies:
            if enemy.alive:
                enemy.update(dt, player)
    
    def remove_dead(self):
        """Remueve enemigos muertos de la lista"""
        self.enemies = [e for e in self.enemies if e.alive]
    
    def get_alive_enemies(self):
        """Retorna lista de enemigos vivos"""
        return [e for e in self.enemies if e.alive]
    
    def get_enemy_count(self):
        """Retorna cantidad de enemigos vivos"""
        return len(self.get_alive_enemies())
    
    def clear_all(self):
        """Elimina todos los enemigos"""
        self.enemies.clear()