# MageDom

MagicDom es un proyecto en desarrollo que combina técnicas de **raycasting al estilo DOOM/Wolfenstein**, control tradicional con teclado y mouse, y **comandos de voz en español** para activar habilidades mágicas. El objetivo es explorar arquitectura modular en Python utilizando **Pygame**, reconocimiento de voz y técnicas gráficas clásicas.

Este repositorio sigue una estructura limpia y escalable, enfocada en buenas prácticas de diseño de software.

---

## 🎯 Objetivo del Proyecto

Desarrollar un prototipo funcional de combate mágico en primera persona, donde el jugador pueda lanzar hechizos mediante comandos de voz.

### Mecánicas Principales

| Elemento         | Descripción                           |
| ---------------- | ------------------------------------- |
| Movimiento       | Teclado + mouse                       |
| Hechizos         | Activación mediante comandos de voz   |
| Estilo visual    | Raycasting 2.5D (retro FPS)           |
| Sistema de juego | Fases, combate, pausa y configuración |

### Fases iniciales

| Fase | Objetivo           | Hechizo       | Comando de voz           |
| ---- | ------------------ | ------------- | ------------------------ |
| 1    | Destruir objetivos | Bola de fuego | "fuego", "bola de fuego" |
| 2    | Eliminar enemigos  | Rayo mágico   | "rayo", "descarga"       |

---

## 🧰 Tecnologías y Librerías

* Python (última versión)
* **Pygame** para la base del juego
* **Raycasting** implementado manualmente
* **SpeechRecognition** con Google Speech API para comandos de voz
* Alternativa offline sugerida: **Vosk**

---

## 📦 Estructura del Proyecto

```
src/
├── main.py
├── game/
├── rendering/
├── entities/
├── input/
├── audio/
└── utils/
```

| Carpeta      | Función                                |
| ------------ | -------------------------------------- |
| `game/`      | Loop principal, estados, configuración |
| `rendering/` | Motor de raycasting y renderizado      |
| `entities/`  | Jugador, enemigos, hechizos            |
| `input/`     | Control por voz y teclado/mouse        |
| `audio/`     | Música y efectos de sonido             |
| `utils/`     | Matemática y carga de assets           |

---

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

```bash
python src/main.py
```

---

## 📚 Recursos Recomendados

### Sprites y Texturas

* [https://opengameart.org](https://opengameart.org)
* [https://itch.io/game-assets](https://itch.io/game-assets)
* [https://kenney.nl/assets](https://kenney.nl/assets)
* [https://textures.com](https://textures.com)

### Sonidos

* [https://freesound.org](https://freesound.org)
* [https://zapsplat.com](https://zapsplat.com)
* [https://opengameart.org](https://opengameart.org)

---

## 🧭 Roadmap

* [ ] HUD y barra de estado
* [ ] IA de enemigos
* [ ] Efectos visuales avanzados para hechizos
* [ ] Optimización del raycasting

---

## 📄 Licencia

Proyecto desarrollado con fines educativos y experimentales.

---

## Autor

Desarrollado como ejercicio de programación y diseño de motor gráfico simple en Python.
