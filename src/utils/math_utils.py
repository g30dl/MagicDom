"""
Funciones matemáticas utilitarias pequeñas.
"""
import math

def clamp(value, minimum, maximum):
	return max(minimum, min(maximum, value))

def lerp(a, b, t):
	return a + (b - a) * t

def deg_to_rad(d):
	return d * (math.pi / 180.0)
