"""
Script de prueba para verificar el reconocimiento de voz.
Ejecuta este script antes de jugar para asegurar que el microfono funciona.
"""
import speech_recognition as sr


def _choose_microphone():
    """Muestra los microfonos disponibles y permite elegir uno por indice."""
    names = sr.Microphone.list_microphone_names()
    print("\nMicrofonos disponibles:")
    for index, name in enumerate(names):
        print(f"  {index}: {name}")
    choice = input("Indice a usar (ENTER para predeterminado): ").strip()
    if not choice:
        return None
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(names):
            return idx
    print("Indice invalido, usando el predeterminado.")
    return None


def test_microphone(timeout=5):
    """Prueba el microfono y reconocimiento de voz."""
    print("=" * 50)
    print("PRUEBA DE RECONOCIMIENTO DE VOZ")
    print("=" * 50)

    recognizer = sr.Recognizer()
    device_index = _choose_microphone()

    print("\n" + "=" * 50)
    print("Preparando microfono...")

    try:
        with sr.Microphone(device_index=device_index) as source:
            print("Calibrando para ruido ambiente (2s)...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Calibracion completada.")

            print("\n" + "=" * 50)
            print("Di algo en ESPANOL...")
            print("=" * 50)

            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=6)
            print("Audio capturado, procesando...")

            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"\nRECONOCIDO: '{text}'")

            comandos = ["bola de fuego", "fuego", "rayo", "trueno", "relampago"]
            comando_encontrado = None
            for comando in comandos:
                if comando in text.lower():
                    comando_encontrado = comando
                    break

            if comando_encontrado:
                print(f"OK - Comando de hechizo detectado: {comando_encontrado}!")
            else:
                print("No se detecto un comando de hechizo valido.")
                print(f"Comandos validos: {', '.join(comandos)}")

            return True

    except sr.WaitTimeoutError:
        print("ERROR: No se detecto audio en el tiempo limite.")
        print("Asegurate de que el microfono este conectado y funcionando.")
        return False
    except sr.UnknownValueError:
        print("ERROR: No se pudo entender el audio.")
        print("Intenta hablar mas claro y cerca del microfono.")
        return False
    except sr.RequestError as e:
        print(f"ERROR: Problema con el servicio de reconocimiento: {e}")
        print("Verifica tu conexion a internet.")
        return False
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        return False


def main():
    print("\nEsta prueba verificara que tu microfono y el")
    print("reconocimiento de voz funcionan correctamente.\n")

    input("Presiona ENTER para comenzar la prueba...")

    success = test_microphone()

    print("\n" + "=" * 50)
    if success:
        print("PRUEBA EXITOSA")
        print("Tu microfono esta funcionando correctamente.")
        print("Puedes ejecutar el juego con: python -m src.main")
    else:
        print("PRUEBA FALLIDA")
        print("Revisa los errores arriba y solucionarlos antes de jugar.")
    print("=" * 50)


if __name__ == "__main__":
    main()
