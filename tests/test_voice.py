"""
Script de prueba para verificar el reconocimiento de voz
Ejecuta este script antes de jugar para asegurarte de que el micrófono funciona
"""
import speech_recognition as sr

def test_microphone():
    """Prueba el micrófono y reconocimiento de voz"""
    print("=" * 50)
    print("PRUEBA DE RECONOCIMIENTO DE VOZ")
    print("=" * 50)
    
    recognizer = sr.Recognizer()
    
    # Listar micrófonos disponibles
    print("\nMicrófonos disponibles:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    # Probar reconocimiento
    print("\n" + "=" * 50)
    print("Preparando micrófono...")
    
    try:
        with sr.Microphone() as source:
            print("Calibrando para ruido ambiente... (espera 2 segundos)")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✓ Calibración completada")
            
            print("\n" + "=" * 50)
            print("Di algo en ESPAÑOL...")
            print("=" * 50)
            
            audio = recognizer.listen(source, timeout=5)
            print("✓ Audio capturado, procesando...")
            
            # Intentar reconocer
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"\n✓ RECONOCIDO: '{text}'")
            
            # Verificar si es un comando válido
            comandos = ["bola de fuego", "fuego", "rayo", "trueno", "relámpago"]
            comando_encontrado = None
            
            for comando in comandos:
                if comando in text.lower():
                    comando_encontrado = comando
                    break
            
            if comando_encontrado:
                print(f"✓ ¡Comando de hechizo detectado: {comando_encontrado}!")
            else:
                print(f"✗ No se detectó un comando de hechizo válido")
                print(f"  Comandos válidos: {', '.join(comandos)}")
            
            return True
            
    except sr.WaitTimeoutError:
        print("✗ ERROR: No se detectó audio en 5 segundos")
        print("  Asegúrate de que el micrófono esté conectado y funcionando")
        return False
    
    except sr.UnknownValueError:
        print("✗ ERROR: No se pudo entender el audio")
        print("  Intenta hablar más claro y cerca del micrófono")
        return False
    
    except sr.RequestError as e:
        print(f"✗ ERROR: Problema con el servicio de reconocimiento: {e}")
        print("  Verifica tu conexión a internet")
        return False
    
    except Exception as e:
        print(f"✗ ERROR inesperado: {e}")
        return False

def main():
    print("\nEsta prueba verificará que tu micrófono y el")
    print("reconocimiento de voz funcionan correctamente.\n")
    
    input("Presiona ENTER para comenzar la prueba...")
    
    success = test_microphone()
    
    print("\n" + "=" * 50)
    if success:
        print("✓ PRUEBA EXITOSA")
        print("Tu micrófono está funcionando correctamente.")
        print("Puedes ejecutar el juego con: python -m src.main")
    else:
        print("✗ PRUEBA FALLIDA")
        print("Revisa los errores arriba y soluciónalos antes de jugar.")
    print("=" * 50)

if __name__ == "__main__":
    main()