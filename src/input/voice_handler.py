"""
Manejador de reconocimiento de voz
Escucha comandos del usuario y los convierte en acciones de hechizos.
Incluye modo continuo para alimentar UI en segundo plano.
"""
import threading
import time
import speech_recognition as sr
from src.game.config import Config


class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self._stop_event = threading.Event()
        self._thread = None

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
                audio = self.recognizer.listen(
                    source,
                    timeout=Config.VOICE_TIMEOUT,
                )

            # Reconocer usando Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(
                    audio, language=Config.VOICE_LANGUAGE
                )
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

    def start_continuous_listening(self, on_text_callback, phrase_time_limit=3):
        """
        Inicia un hilo en segundo plano que escucha continuamente y llama
        a `on_text_callback(texto)` cada vez que reconoce algo.
        """

        if self._thread and self._thread.is_alive():
            return  # ya corriendo

        self._stop_event.clear()

        def _worker():
            while not self._stop_event.is_set():
                try:
                    with self.microphone as source:
                        audio = self.recognizer.listen(
                            source,
                            timeout=Config.VOICE_TIMEOUT,
                            phrase_time_limit=phrase_time_limit,
                        )
                    try:
                        text = self.recognizer.recognize_google(
                            audio, language=Config.VOICE_LANGUAGE
                        )
                        if text:
                            on_text_callback(text)
                    except sr.UnknownValueError:
                        # silencio o no entendible — ignorar
                        pass
                    except sr.RequestError as e:
                        print(f"[Voz] Error del servicio: {e}")
                        time.sleep(0.5)
                except sr.WaitTimeoutError:
                    # No hubo audio dentro del timeout; seguir intentando
                    continue
                except Exception as e:
                    print(f"[Voz] Error escuchando: {e}")
                    time.sleep(0.5)

        self._thread = threading.Thread(target=_worker, daemon=True)
        self._thread.start()

    def stop(self):
        """Detiene el hilo de escucha continua, si existe."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

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
            text = self.recognizer.recognize_google(
                audio, language=Config.VOICE_LANGUAGE
            )
            print(f"Reconocido: '{text}'")
            return text
        except Exception as e:
            print(f"Error: {e}")
            return None
