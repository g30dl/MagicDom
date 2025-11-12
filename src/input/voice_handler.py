"""
Manejador de reconocimiento de voz
Escucha comandos del usuario y los convierte en acciones de hechizos
"""
import speech_recognition as sr
from src.game.config import Config

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Ajustar para ruido ambiente
        with self.microphone as source:
            print("Calibrando micrófono...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def listen_for_spell(self):
        """
        Escucha un comando de voz y lo convierte en un hechizo
        Retorna el nombre del hechizo o None si no se reconoce
        """
        try:
            with self.microphone as source:
                print("Escuchando... (di el nombre del hechizo)")
                audio = self.recognizer.listen(source, timeout=Config.VOICE_TIMEOUT)
            
            # Reconocer usando Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio, language=Config.VOICE_LANGUAGE)
                print(f"Reconocido: '{text}'")
                
                # Convertir texto a comando de hechizo
                return self.text_to_spell(text.lower())
            
            except sr.UnknownValueError:
                print("No se pudo entender el audio")
                return None
            except sr.RequestError as e:
                print(f"Error con el servicio de reconocimiento: {e}")
                return None
        
        except Exception as e:
            print(f"Error en reconocimiento de voz: {e}")
            return None
    
    def text_to_spell(self, text):
        """
        Convierte texto reconocido en nombre de hechizo
        """
        # Buscar coincidencias en el diccionario de hechizos
        for keyword, spell_name in Config.SPELLS.items():
            if keyword in text:
                return spell_name
        
        print(f"Comando no reconocido: '{text}'")
        print(f"Comandos válidos: {', '.join(Config.SPELLS.keys())}")
        return None
    
    def test_microphone(self):
        """Prueba el micrófono y muestra lo que reconoce"""
        print("Prueba de micrófono - Di algo...")
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5)
            text = self.recognizer.recognize_google(audio, language=Config.VOICE_LANGUAGE)
            print(f"Reconocido: '{text}'")
            return text
        except Exception as e:
            print(f"Error: {e}")
            return None