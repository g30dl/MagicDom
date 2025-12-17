"""
Entidad de enemigo con IA simple, pathfinding BFS y animaciones por estado.
Incluye soporte de billboard para el renderizador 3D.
"""
import math
import os
import random
from collections import deque

import pygame
from src.game.config import Config


def _frame_sort_key(name: str):
    """Ordena frames por número si es posible (0.png, 1.png, ...)."""
    base, _ = os.path.splitext(name)
    try:
        return int(base)
    except ValueError:
        return base


class SpriteAnimation:
    """Controla una secuencia de frames con duración fija por frame."""

    def __init__(self, frames, frame_time=0.12, loop=True):
        self.frames = frames or []
        self.frame_time = max(0.01, float(frame_time))
        self.loop = loop
        self.time = 0.0
        self.index = 0
        self.finished = False

    def reset(self):
        self.time = 0.0
        self.index = 0
        self.finished = False

    def update(self, dt: float):
        if not self.frames or self.finished:
            return self.get_frame()

        self.time += dt
        while self.time >= self.frame_time and not self.finished:
            self.time -= self.frame_time
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index %= len(self.frames)
                else:
                    self.index = len(self.frames) - 1
                    self.finished = True
        return self.get_frame()

    def get_frame(self):
        if not self.frames:
            return None
        return self.frames[self.index]


def _make_placeholder(color=(255, 0, 255)):
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    surf.fill((*color, 220))
    return surf


def _load_frame(path, fallback):
    try:
        if os.path.exists(path):
            return pygame.image.load(path).convert_alpha()
    except Exception:
        pass
    return fallback


def _load_frames_from_dir(path, fallback):
    if not path or not os.path.isdir(path):
        return []
    files = [f for f in os.listdir(path) if f.lower().endswith(".png")]
    files.sort(key=_frame_sort_key)
    frames = []
    for name in files:
        frame = _load_frame(os.path.join(path, name), fallback)
        frames.append(frame)
    return frames


ENEMY_PRESETS = {
    "rockbad": {
        "asset_path": os.path.join("assets", "enemies", "RockBad"),
        "health": 120,
        "damage": 12,
        "speed": 1.6,
        "attack_cooldown": 1.3,
        "attack_range": Config.TILE_SIZE * 0.9,
        "detection_range": Config.TILE_SIZE * 9,
        "radius": Config.TILE_SIZE * 0.2,
        "sprite_scale": 1.1,
    },
    "cyber_demon": {
        "asset_path": os.path.join("assets", "enemies", "cyber_demon"),
        "health": 260,
        "damage": 18,
        "speed": 1.2,
        "attack_cooldown": 1.4,
        "attack_range": Config.TILE_SIZE * 2.4,
        "detection_range": Config.TILE_SIZE * 11,
        "radius": Config.TILE_SIZE * 0.22,
        "sprite_scale": 1.25,
    },
    "basic": {
        "asset_path": os.path.join("assets", "enemies", "RockBad"),
        "health": 50,
        "damage": 8,
        "speed": 1.5,
        "attack_cooldown": 1.5,
        "attack_range": Config.TILE_SIZE * 0.8,
        "detection_range": Config.TILE_SIZE * 7,
        "radius": Config.TILE_SIZE * 0.18,
        "sprite_scale": 1.0,
    },
}


class Enemy:
    def __init__(self, x, y, enemy_type="basic", game_map=None, is_boss=False):
        self.x = float(x)
        self.y = float(y)
        self.type = enemy_type.lower()
        self.alive = True
        self._dying = False
        self.death_animation_done = False
        self.game_map = game_map
        self.is_boss = bool(is_boss)

        preset = ENEMY_PRESETS.get(self.type, ENEMY_PRESETS["basic"])
        self.health = preset.get("health", 50)
        self.max_health = self.health
        self.damage = preset.get("damage", 10)
        self.speed = preset.get("speed", 1.4)
        self.attack_cooldown_time = preset.get("attack_cooldown", 1.5)
        self.attack_cooldown = 0.0
        self.attack_range = preset.get("attack_range", 100)
        self.detection_range = preset.get("detection_range", 500)
        self.collision_radius = preset.get("radius", 18)
        self.sprite_scale = preset.get("sprite_scale", 1.0)
        self.angle = 0.0
        self.frozen_timer = 0.0

        # IA y pathfinding
        self.state = "idle"  # idle, walk, attack, pain, death
        self.path = []
        self.path_timer = 0.0
        self.path_recalc_interval = 0.35
        self._pain_timer = 0.0
        self.has_line_of_sight = False

        # Animaciones
        asset_path = preset.get("asset_path")
        self.directional_idle = self._load_directional_variants(asset_path)
        self.animations = self._load_animations(asset_path)
        self._current_anim = None
        self._current_anim_name = None
        self._switch_animation("idle")

    # ------------------------------------------------------------------
    # Carga de sprites / animaciones
    # ------------------------------------------------------------------
    def _load_animations(self, asset_path):
        base_frame = _load_frame(os.path.join(asset_path or "", "normal.png"), _make_placeholder())
        # Idle: si hay front en direccionales, úsalo; si no, base_frame
        idle_frame = None
        if self.directional_idle:
            idle_frame = self.directional_idle.get("front")
        if idle_frame is None:
            idle_frame = base_frame
        self.frozen_frame = _load_frame(os.path.join(asset_path or "", "frost.png"), base_frame)

        walk_frames = _load_frames_from_dir(os.path.join(asset_path or "", "walk"), base_frame) or [base_frame]
        walk_frames = self._stretch_walk_frames(walk_frames)
        walk_frame_time = 0.1  # pasos rápidos entre frames, ciclo total lento por repetición

        anims = {}
        anims["idle"] = SpriteAnimation([idle_frame], frame_time=0.25, loop=True)
        anims["walk"] = SpriteAnimation(walk_frames, frame_time=walk_frame_time, loop=True)
        anims["attack"] = SpriteAnimation(
            _load_frames_from_dir(os.path.join(asset_path or "", "attack"), base_frame) or [base_frame],
            frame_time=0.2,
            loop=True,
        )
        anims["pain"] = SpriteAnimation(
            _load_frames_from_dir(os.path.join(asset_path or "", "pain"), base_frame) or [base_frame],
            frame_time=0.18,
            loop=False,
        )
        death_frames = _load_frames_from_dir(os.path.join(asset_path or "", "death"), base_frame) or [base_frame]
        anims["death"] = SpriteAnimation(death_frames, frame_time=0.18, loop=False)
        return anims

    def _load_directional_variants(self, asset_path):
        """Carga variantes direccionales para idle (front, back, left, right, diagonales)."""
        names = {
            "front": "front.png",
            "back": "back.png",
            "left": "left.png",
            "right": "right.png",
            "front_left": "front_left.png",
            "front_right": "front_right.png",
            "back_left": "back_left.png",
            "back_right": "back_right.png",
        }
        variants = {}
        for key, filename in names.items():
            path = os.path.join(asset_path or "", "idle", filename)
            frame = _load_frame(path, None)
            if frame is not None:
                variants[key] = frame
        if not variants:
            return {}
        # Completar faltantes con alguna variante existente (preferir front/back)
        defaults = [
            variants.get("front"),
            variants.get("back"),
            variants.get("left"),
            variants.get("right"),
        ]
        fallback = next((v for v in defaults if v is not None), _make_placeholder())
        for key in names.keys():
            variants.setdefault(key, fallback)
        return variants

    def _stretch_walk_frames(self, frames):
        """
        Crea una secuencia con pausas largas en el primer frame y transiciones rápidas.
        Ejemplo con 3 frames: [0...0, 1,1, 2,2] -> ciclo lento pero cambio rápido.
        """
        if not frames:
            return frames
        if len(frames) < 3:
            return frames
        hold = 35  # cuántas veces repetir el primer frame (ciclo más corto)
        stretched = [frames[0]] * hold + [frames[1]] * 2 + [frames[2]] * 2
        return stretched

    def _get_animation(self, state):
        return self.animations.get(state) or self.animations.get("idle")

    def _switch_animation(self, state):
        if self._current_anim_name == state:
            return
        anim = self._get_animation(state)
        if anim is None:
            return
        anim.reset()
        self._current_anim = anim
        self._current_anim_name = state

    def _update_animation(self, dt):
        if self._current_anim:
            self._current_anim.update(dt)

    def get_current_frame(self):
        if self._current_anim:
            frame = self._current_anim.get_frame()
            if frame is not None:
                return frame
        return _make_placeholder()

    def get_frame_for_view(self, camera_angle):
        """
        Devuelve el frame actual considerando el ángulo de cámara alrededor del enemigo.
        camera_angle: ángulo (rad) desde el enemigo hacia la cámara (player).
        """
        if self._current_anim_name == "idle" and self.directional_idle:
            delta = (camera_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
            key = self._direction_key(delta)
            frame = self.directional_idle.get(key)
            if frame is not None:
                return frame
        return self.get_current_frame()

    def _direction_key(self, delta):
        """Mapea delta de -pi..pi a una de 8 direcciones cardinales/diagonales."""
        octants = [
            "front",
            "front_right",
            "right",
            "back_right",
            "back",
            "back_left",
            "left",
            "front_left",
        ]
        step = math.pi / 4
        idx = int(round(delta / step)) % 8
        return octants[idx]

    # ------------------------------------------------------------------
    # IA y navegación
    # ------------------------------------------------------------------
    def _tile_from_pos(self, x, y):
        return int(x // Config.TILE_SIZE), int(y // Config.TILE_SIZE)

    def _is_walkable(self, tile_x, tile_y):
        if self.game_map is None:
            return False
        rows = len(self.game_map)
        cols = len(self.game_map[0]) if rows else 0
        if tile_x < 0 or tile_x >= cols or tile_y < 0 or tile_y >= rows:
            return False
        return self.game_map[tile_y][tile_x] == 0

    def _tile_clear_for_radius(self, tile_x, tile_y):
        """Comprueba si el radio del enemigo cabe en ese tile sin tocar paredes vecinas."""
        if not self._is_walkable(tile_x, tile_y):
            return False
        margin_tiles = 1  # margen de 1 tile alrededor para radios grandes
        rows = len(self.game_map)
        cols = len(self.game_map[0]) if rows else 0
        for dy in range(-margin_tiles, margin_tiles + 1):
            for dx in range(-margin_tiles, margin_tiles + 1):
                nx, ny = tile_x + dx, tile_y + dy
                if nx < 0 or nx >= cols or ny < 0 or ny >= rows:
                    return False
                if self.game_map[ny][nx] != 0:
                    return False
        return True

    def _collides(self, x, y):
        if self.game_map is None:
            return False
        offsets = [
            (self.collision_radius, 0),
            (-self.collision_radius, 0),
            (0, self.collision_radius),
            (0, -self.collision_radius),
            (self.collision_radius * 0.7, self.collision_radius * 0.7),
            (-self.collision_radius * 0.7, self.collision_radius * 0.7),
            (self.collision_radius * 0.7, -self.collision_radius * 0.7),
            (-self.collision_radius * 0.7, -self.collision_radius * 0.7),
        ]
        for ox, oy in offsets:
            tx = int((x + ox) // Config.TILE_SIZE)
            ty = int((y + oy) // Config.TILE_SIZE)
            if not self._is_walkable(tx, ty):
                return True
        return False

    def _recalc_path(self, target_tile):
        if self.game_map is None:
            self.path = []
            return
        start = self._tile_from_pos(self.x, self.y)
        goal = target_tile
        if start == goal:
            self.path = []
            return

        queue = deque([start])
        came_from = {start: None}
        rows = len(self.game_map)
        cols = len(self.game_map[0]) if rows else 0
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                break
            for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if 0 <= nx < cols and 0 <= ny < rows and self._tile_clear_for_radius(nx, ny) and (nx, ny) not in came_from:
                    came_from[(nx, ny)] = (cx, cy)
                    queue.append((nx, ny))

        if goal not in came_from:
            self.path = []
            return

        rev_path = []
        cur = goal
        while cur != start:
            rev_path.append(cur)
            cur = came_from.get(cur)
            if cur is None:
                break
        rev_path.reverse()
        self.path = rev_path

    def _move_towards_player(self, dt, player):
        self.path_timer -= dt
        player_tile = self._tile_from_pos(player.x, player.y)

        direct_chase = self.has_line_of_sight
        if direct_chase:
            self.path = []
        else:
            if self.path_timer <= 0 or not self.path or self.path[-1] != player_tile:
                self._recalc_path(player_tile)
                self.path_timer = self.path_recalc_interval

        target_x, target_y = player.x, player.y
        if not direct_chase and self.path:
            tile_x, tile_y = self.path[0]
            target_x = tile_x * Config.TILE_SIZE + Config.TILE_SIZE * 0.5
            target_y = tile_y * Config.TILE_SIZE + Config.TILE_SIZE * 0.5

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0.0001:
            dx /= dist
            dy /= dist
            self.angle = math.atan2(dy, dx)
        step = self.speed * dt * 60.0
        new_x = self.x + dx * step
        new_y = self.y + dy * step

        if not self._collides(new_x, self.y):
            self.x = new_x
        if not self._collides(self.x, new_y):
            self.y = new_y

        if not direct_chase and self.path:
            target_tile_center = (
                self.path[0][0] * Config.TILE_SIZE + Config.TILE_SIZE * 0.5,
                self.path[0][1] * Config.TILE_SIZE + Config.TILE_SIZE * 0.5,
            )
            if math.hypot(self.x - target_tile_center[0], self.y - target_tile_center[1]) < self.collision_radius:
                self.path.pop(0)

    def _has_line_of_sight(self, player):
        if self.game_map is None:
            return False
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        if distance <= 0.001 or distance > self.detection_range * 1.2:
            return False

        steps = max(1, int(distance / (Config.TILE_SIZE * 0.6)))
        for i in range(1, steps + 1):
            t = i / steps
            px = self.x + dx * t
            py = self.y + dy * t
            tile_x, tile_y = self._tile_from_pos(px, py)
            if not self._is_walkable(tile_x, tile_y):
                return False
        return True

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def update(self, dt, player, game_map=None):
        if game_map is not None:
            self.game_map = game_map

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.frozen_timer > 0:
            self.frozen_timer -= dt
            self.state = "frozen"
            # Sin animación ni cambio de frame: se queda en el frame actual
            return

        if self.state == "death":
            self._update_animation(dt)
            if self._current_anim and self._current_anim.finished:
                self.death_animation_done = True
            return

        if not self.alive and not self._dying:
            self._switch_animation("death")
            self.state = "death"
            self._dying = True
            return

        self.has_line_of_sight = self._has_line_of_sight(player)
        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)

        if self._pain_timer > 0:
            self._pain_timer -= dt
            self.state = "pain"
            self._switch_animation("pain")
            self._update_animation(dt)
            return

        if dist_to_player <= self.attack_range and self.has_line_of_sight:
            self.state = "attack"
            self._switch_animation("attack")
            self.angle = math.atan2(player.y - self.y, player.x - self.x)
            if self.attack_cooldown <= 0:
                self.attack_player(player)
                self.attack_cooldown = self.attack_cooldown_time
            self._update_animation(dt)
            return

        if self.has_line_of_sight and dist_to_player <= self.detection_range:
            self.state = "walk"
            self._switch_animation("walk")
            self._move_towards_player(dt, player)
        else:
            self.state = "idle"
            self._switch_animation("idle")
            self.idle_behavior(dt)

        self._update_animation(dt)

    def idle_behavior(self, dt):
        """Pequeña deriva aleatoria cuando está en idle."""
        if random.random() < 0.02:
            angle = random.uniform(0, math.tau)
            step = self.speed * dt * 20.0
            new_x = self.x + math.cos(angle) * step
            new_y = self.y + math.sin(angle) * step
            if not self._collides(new_x, new_y):
                self.x = new_x
                self.y = new_y

    def attack_player(self, player):
        """Ataca al jugador con daño fijo."""
        player.take_damage(self.damage)
        print(f"Enemigo {self.type} ataca. Daño: {self.damage}")

    def take_damage(self, damage, damage_type=None):
        """Recibe daño y activa animación de dolor."""
        multiplier = 1.0
        if damage_type == "fireball" and self.type == "tank":
            multiplier = 1.5
        elif damage_type == "lightning" and self.type == "fast":
            multiplier = 1.5
        elif damage_type == "frost":
            # Congelar por 3.5 segundos al recibir frost
            self.frozen_timer = max(self.frozen_timer, 3.5)

        actual_damage = int(damage * multiplier)
        self.health -= actual_damage
        print(f"Enemigo {self.type} recibe {actual_damage} de daño")

        if self.health <= 0:
            self.die()
        else:
            self._pain_timer = 0.35
            self._switch_animation("pain")

    def die(self):
        """Muerte del enemigo (dispara animación de death)."""
        if not self.alive:
            return
        self.alive = False
        self.health = 0
        self.state = "death"
        self._switch_animation("death")
        print(f"Enemigo {self.type} eliminado")

    def get_position(self):
        return (self.x, self.y)

    def get_health_percentage(self):
        return self.health / self.max_health if self.max_health > 0 else 0

    def is_renderable(self):
        if self.state == "death":
            return not self.death_animation_done
        return True

    def should_remove(self):
        return self.state == "death" and self.death_animation_done


class EnemyManager:
    """Administrador de todos los enemigos en el nivel."""

    def __init__(self, game_map=None):
        self.enemies = []
        self.game_map = game_map

    def set_map(self, game_map):
        self.game_map = game_map
        for enemy in self.enemies:
            enemy.game_map = game_map

    def add_enemy(self, x, y, enemy_type="rockbad", is_boss=False):
        enemy = Enemy(x, y, enemy_type, game_map=self.game_map, is_boss=is_boss)
        self.enemies.append(enemy)
        return enemy

    def update_all(self, dt, player):
        for enemy in self.enemies:
            enemy.update(dt, player, self.game_map)

    def remove_dead(self):
        self.enemies = [e for e in self.enemies if not e.should_remove()]

    def get_alive_enemies(self):
        return [e for e in self.enemies if e.alive]

    def get_renderable_enemies(self):
        return [e for e in self.enemies if e.is_renderable()]

    def get_enemy_count(self):
        return len(self.get_alive_enemies())

    def get_boss_alive_count(self):
        return len([e for e in self.enemies if getattr(e, "is_boss", False) and e.alive])

    def clear_all(self):
        self.enemies.clear()
