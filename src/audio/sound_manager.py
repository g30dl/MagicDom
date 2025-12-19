"""Sistema de gestion de audio para musica y efectos."""
import os
import pygame
from src.game.config import Config


class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            self.enabled = False
            print(f"[Audio] Mixer no disponible: {e}")
            return

        self.music_tracks = {}
        self.sound_effects = {}
        self.track_volume_scale = {
            "background": getattr(Config, "BACKGROUND_VOLUME_SCALE", 1.0),
            "playing_theme": getattr(Config, "BACKGROUND_VOLUME_SCALE", 1.0),
            "playing": getattr(Config, "BACKGROUND_VOLUME_SCALE", 1.0),
        }
        self.current_track = None

        self.load_audio()

        try:
            pygame.mixer.music.set_volume(Config.MUSIC_VOLUME)
        except Exception as e:
            print(f"[Audio] No se pudo ajustar volumen: {e}")
            self.enabled = False

    def _register_music_track(self, name, filepath, override=False):
        """
        Registra una pista si existe. Si override es True reemplaza la previa.
        """
        if not os.path.exists(filepath):
            print(f"Advertencia: No se encontro {filepath}")
            return
        if name in self.music_tracks and not override:
            return
        self.music_tracks[name] = filepath
        print(f"Registrada musica: {name}")

    def load_audio(self):
        """Carga archivos de audio desde assets/music/sounds y assets/music."""
        if not self.enabled:
            return

        sounds_path = os.path.join("assets", "music", "sounds")
        music_path = "assets/music"

        os.makedirs(sounds_path, exist_ok=True)
        os.makedirs(music_path, exist_ok=True)

        sound_files = {
            "fireball": "fire.wav",
            "hit": "fire.wav",
            "frost": "fire.wav",
            "lightning": "lightning.mp3",
            "healing": "heal.wav",
            "heal": "heal.wav",
            "speed": "speed.wav",  # boost de velocidad
            "romper_pared": "romper_pared.wav",
            "menu_click": "clic.wav",
            "error": "controller_button_press_2.wav",
            "death": "death.wav",
            "lost": "death.wav",
        }

        for name, filename in sound_files.items():
            filepath = os.path.join(sounds_path, filename)
            if os.path.exists(filepath):
                try:
                    self.sound_effects[name] = pygame.mixer.Sound(filepath)
                    self.sound_effects[name].set_volume(Config.SFX_VOLUME)
                    print(f"Cargado efecto: {name}")
                except Exception as e:
                    print(f"Error cargando {filename}: {e}")
            else:
                print(f"Advertencia: No se encontro {filepath}")

        # Efectos de enemigos ubicados en assets/music/<enemigo>/attack.*
        enemy_sfx_candidates = {
            "rockybad_attack": [
                os.path.join("assets", "music", "Rockbad", "attack.wav"),
                os.path.join("assets", "music", "rockbad", "attack.wav"),
                os.path.join("assets", "music", "rockybad", "attack.wav"),
            ],
            "cyber_demon_hit": [
                os.path.join("assets", "music", "Cyber_demon", "hit.wav"),
                os.path.join("assets", "music", "cyber_demon", "hit.wav"),
            ],
        }
        for name, paths in enemy_sfx_candidates.items():
            filepath = next((p for p in paths if os.path.exists(p)), None)
            if filepath:
                try:
                    self.sound_effects[name] = pygame.mixer.Sound(filepath)
                    self.sound_effects[name].set_volume(Config.SFX_VOLUME)
                    print(f"Cargado efecto: {name}")
                except Exception as e:
                    print(f"Error cargando {filepath}: {e}")
            else:
                print(f"Advertencia: No se encontro ruta para {name}: {paths[0]}")

        base_music = {
            "background": os.path.join(music_path, "background.mp3"),
            "menu": os.path.join(music_path, "menu.mp3"),
        }
        for name, filepath in base_music.items():
            self._register_music_track(name, filepath)

        theme_path = os.path.join(music_path, "theme")
        os.makedirs(theme_path, exist_ok=True)
        theme_music = {
            "menu_theme": os.path.join(theme_path, "menu.mp3"),
            "menu": os.path.join(theme_path, "menu.mp3"),
            "playing_theme": os.path.join(theme_path, "playing.mp3"),
            "playing": os.path.join(theme_path, "playing.mp3"),
            "background": os.path.join(theme_path, "playing.mp3"),
            "victory": os.path.join(theme_path, "victory.mp3"),
        }
        for name, filepath in theme_music.items():
            self._register_music_track(name, filepath, override=True)

    def play_sfx(self, sound_name):
        """Reproduce un efecto de sonido."""
        if not self.enabled:
            return
        if sound_name in self.sound_effects:
            self.sound_effects[sound_name].play()
        else:
            print(f"Efecto de sonido no encontrado: {sound_name}")

    def play_music(self, track_name, loops=-1):
        """
        Reproduce musica de fondo. loops=-1 significa loop infinito.
        """
        if not self.enabled:
            return
        if track_name in self.music_tracks:
            try:
                pygame.mixer.music.load(self.music_tracks[track_name])
                self.current_track = track_name
                self._apply_track_volume(track_name)
                pygame.mixer.music.play(loops)
                print(f"Reproduciendo musica: {track_name}")
            except Exception as e:
                self.current_track = None
                print(f"Error reproduciendo musica {track_name}: {e}")
        else:
            print(f"Pista de musica no encontrada: {track_name}")

    def stop_music(self):
        """Detiene la musica actual."""
        if self.enabled:
            pygame.mixer.music.stop()
            self.current_track = None

    def pause_music(self):
        """Pausa la musica actual."""
        if self.enabled:
            pygame.mixer.music.pause()

    def resume_music(self):
        """Resume la musica pausada."""
        if self.enabled:
            pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        """Ajusta el volumen de la musica (0.0 a 1.0)."""
        Config.MUSIC_VOLUME = max(0.0, min(1.0, volume))
        if self.enabled:
            self._apply_track_volume(self.current_track)

    def set_sfx_volume(self, volume):
        """Ajusta el volumen de los efectos de sonido (0.0 a 1.0)."""
        Config.SFX_VOLUME = max(0.0, min(1.0, volume))
        if self.enabled:
            for sound in self.sound_effects.values():
                sound.set_volume(Config.SFX_VOLUME)

    def _apply_track_volume(self, track_name):
        """Aplica el volumen global con el factor personalizado de la pista."""
        if not self.enabled:
            return
        scale = self.track_volume_scale.get(track_name, 1.0) if track_name else 1.0
        volume = max(0.0, min(1.0, Config.MUSIC_VOLUME * scale))
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception as e:
            print(f"[Audio] No se pudo ajustar volumen: {e}")
