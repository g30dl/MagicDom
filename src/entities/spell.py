"""
Stub mínimo para hechizos (Spell).
"""
class Spell:
	def __init__(self, name: str, damage: int = 10, speed: float = 5.0):
		self.name = name
		self.damage = int(damage)
		self.speed = float(speed)

	def update(self, dt: float):
		# Placeholder para mover o aplicar efectos
		pass

	def on_hit(self, target):
		# Aplicar daño al objetivo si tiene `take_damage`
		try:
			target.take_damage(self.damage)
		except Exception:
			pass
