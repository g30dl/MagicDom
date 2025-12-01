# MagicDom (Mage Arena 3D)

Juego experimental estilo raycasting (DOOM/Wolfenstein) escrito en Python + Pygame, con control por teclado y mouse mas comandos de voz en espanol para lanzar hechizos.

## Caracteristicas
- Render 3D por raycasting con minimapa, punto de mira, overlay de sangre y manos en HUD.
- Comandos de voz en espanol (Google Speech) para castear hechizos; el texto reconocido aparece en pantalla.
- Hechizos con particulas y sonidos (fireball, lightning) y spawns de enemigos configurables en el mapa.
- Administrador de audio para musica y efectos; valores ajustables en `src/game/config.py`.
- Mapa por defecto en `src/rendering/map_manager.py` con texturas en `assets/`.

## Requisitos previos
- Python 3.10 o superior.
- Windows, macOS o Linux con soporte para Pygame.
- Microfono e internet si quieres usar reconocimiento de voz.
- Dependencias listadas en `requirements.txt`: pygame, SpeechRecognition, pyaudio, pipwin, numpy. En Linux puede requerir `portaudio` (por ejemplo `sudo apt-get install portaudio19-dev` antes de instalar pyaudio).

## Instalacion rapida (Windows)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m pip install pipwin       # solo si pipwin no quedo instalado
python -m pipwin install pyaudio   # instala binarios de pyaudio
```
En macOS/Linux activa el entorno (`source .venv/bin/activate`) y, si pipwin no esta disponible, instala pyaudio con `pip install pyaudio` tras tener portaudio en el sistema.

## Probar el microfono
```bash
python -m tests.test_voice
```
El script lista microfonos, calibra para ruido ambiente y verifica que pueda detectar un comando de hechizo.

## Ejecutar el juego
```bash
python -m src.main
```
- Menu: ENTER para empezar, ESC para salir.
- Juego: WASD mover, mouse mirar, SHIFT sprint, ESC pausa/reanudar, R reanuda desde pausa, R en Game Over reinicia.

## Comandos de voz disponibles
- "bola de fuego" / "fuego"
- "rayo" / "trueno" / "relampago"
Si no hay microfono o no hay conexion, el juego sigue corriendo pero la UI mostrara que la voz esta desactivada.

## Estructura rapida del repo
- `src/main.py`: punto de entrada del juego.
- `src/game/`: loop principal, estados y configuracion global.
- `src/rendering/`: renderer, raycaster, HUD, texturas y mapa.
- `src/entities/`: player, enemigos, hechizos y particulas.
- `src/input/`: manejadores de teclado/mouse y voz.
- `assets/`: sonidos, musica, sprites y texturas.
- `tests/test_voice.py`: chequeo simple del microfono y reconocimiento.

## Notas utiles
- Ajusta constantes (FOV, velocidad, volumenes, hechizos) en `src/game/config.py`.
- Los efectos de sonido o musica son opcionales; si faltan archivos, `SoundManager` muestra advertencias pero no detiene el juego.
