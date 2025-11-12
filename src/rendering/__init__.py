"""
Paquete de renderizado.

Exporta los módulos principales del paquete rendering.
"""

from . import renderer
from . import raycaster
from . import textures

__all__ = [
	'renderer',
	'raycaster',
	'textures',
]
"""
Paquete de renderizado.

Se exponen los submódulos principales (renderer, raycaster, textures).
Importamos los módulos en lugar de nombres concretos para evitar errores
si algún archivo aún está vacío.
"""

from . import renderer
from . import raycaster
from . import textures

__all__ = [
	'renderer',
	'raycaster',
	'textures',
]
