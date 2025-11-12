"""
Entidad Player mínima (stub).

Contiene propiedades básicas y métodos `move`, `rotate`, `take_damage` usados
por el resto del motor para evitar import errors mientras se desarrolla la clase
completa.
"""
import math

class Player:
	def __init__(self, x=0, y=0, angle=0.0, health=100):
		self.x = float(x)
		self.y = float(y)
		self.angle = float(angle)
		self.health = int(health)
		self.max_health = int(health)

	def move(self, forward: float, strafe: float, dt: float, speed: float = 2.0):
		"""Mueve al jugador usando movimiento relativo a su ángulo."""
		# Movimiento multiplicado por 60 para que los stubs funcionen con dt pequeño
		self.x += (math.cos(self.angle) * forward - math.sin(self.angle) * strafe) * speed * dt * 60
		self.y += (math.sin(self.angle) * forward + math.cos(self.angle) * strafe) * speed * dt * 60

	def rotate(self, delta: float, dt: float, rot_speed: float = 0.03):
		"""Rota al jugador. delta puede ser cantidad de ejes o ya un delta en radianes."""
		try:
			self.angle += float(delta) * rot_speed * dt * 60
		except Exception:
			# Si delta ya es un valor en radianes (por ejemplo mouse_dx*sens)
			try:
				self.angle += delta
			except Exception:
				pass

	def take_damage(self, damage: int):
		self.health -= int(damage)
		if self.health < 0:
			self.health = 0

	def is_alive(self) -> bool:
		return self.health > 0

