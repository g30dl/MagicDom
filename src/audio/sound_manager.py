"""
Sistema de gestión de audio
Maneja música y efectos de sonido
"""
import pygame
import os
from src.game.config import Config

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        # Diccionarios para almacenar sonidos
        self.music_tracks = {}
        self.sound_effects = {}
        
        # Cargar recursos de audio
        self.load_audio()
        
        # Configurar volúmenes
        pygame.mixer.music.set_volume(Config.MUSIC_VOLUME)
    
    def load_audio(self):
        """
        Carga archivos de audio desde la carpeta assets/sounds
        """
        # Rutas de audio
        sounds_path = "assets/sounds"
        music_path = "assets/music"
        
        # Crear directorios si no existen
        os.makedirs(sounds_path, exist_ok=True)
        os.makedirs(music_path, exist_ok=True)
        
        # Intentar cargar efectos de sonido
        sound_files = {
            "fireball": "fireball.wav",
            "lightning": "lightning.wav",
            "error": "error.wav",
            "hit": "hit.wav",
            "death": "death.wav",
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
                print(f"Advertencia: No se encontró {filepath}")
        
        # Música de fondo
        music_files = {
            "background": "background.mp3",
            "menu": "menu.mp3",
        }
        
        for name, filename in music_files.items():
            filepath = os.path.join(music_path, filename)
            if os.path.exists(filepath):
                self.music_tracks[name] = filepath
                print(f"Registrada música: {name}")
            else:
                print(f"Advertencia: No se encontró {filepath}")
    
    def play_sfx(self, sound_name):
        """Reproduce un efecto de sonido"""
        if sound_name in self.sound_effects:
            self.sound_effects[sound_name].play()
        else:
            print(f"Efecto de sonido no encontrado: {sound_name}")
    
    def play_music(self, track_name, loops=-1):
        """
        Reproduce música de fondo
        loops=-1 significa loop infinito
        """
        if track_name in self.music_tracks:
            try:
                pygame.mixer.music.load(self.music_tracks[track_name])
                pygame.mixer.music.play(loops)
                print(f"Reproduciendo música: {track_name}")
            except Exception as e:
                print(f"Error reproduciendo música {track_name}: {e}")
        else:
            print(f"Pista de música no encontrada: {track_name}")
    
    def stop_music(self):
        """Detiene la música actual"""
        pygame.mixer.music.stop()
    
    def pause_music(self):
        """Pausa la música actual"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Resume la música pausada"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume):
        """Ajusta el volumen de la música (0.0 a 1.0)"""
        Config.MUSIC_VOLUME = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(Config.MUSIC_VOLUME)
    
    def set_sfx_volume(self, volume):
        """Ajusta el volumen de los efectos de sonido (0.0 a 1.0)"""
        Config.SFX_VOLUME = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(Config.SFX_VOLUME)