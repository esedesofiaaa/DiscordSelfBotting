#!/usr/bin/env python3
"""
Script de prueba para el sistema de heartbeats
Permite probar la conexión con Healthchecks.io sin ejecutar el bot completo
"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from heartbeat_system import HeartbeatSystem

# Cargar variables de entorno
load_dotenv()


async def test_heartbeat():
    """Función principal de prueba"""
    print("🧪 Probando Sistema de Heartbeats")
    print("=" * 50)
    
    # Obtener URL de configuración
    heartbeat_url = os.getenv('HEALTHCHECKS_PING_URL')
    
    if not heartbeat_url:
        print("❌ Error: HEALTHCHECKS_PING_URL no está configurado")
        print("   Asegúrate de tener la URL en tu archivo .env")
        return False
    
    print(f"📍 URL de ping: {heartbeat_url[:50]}{'...' if len(heartbeat_url) > 50 else ''}")
    
    # Crear sistema de heartbeats
    heartbeat = HeartbeatSystem(heartbeat_url)
    
    # Prueba 1: Ping de inicio
    print("\n🚀 Prueba 1: Ping de inicio")
    result = await heartbeat.send_ping("start", "Test de inicio del sistema")
    print(f"   Resultado: {'✅ Éxito' if result else '❌ Error'}")
    
    # Prueba 2: Ping de éxito
    print("\n✅ Prueba 2: Ping de éxito")
    result = await heartbeat.send_ping("success", "Test de funcionamiento normal")
    print(f"   Resultado: {'✅ Éxito' if result else '❌ Error'}")
    
    # Prueba 3: Ping manual
    print("\n📤 Prueba 3: Ping manual")
    result = await heartbeat.send_manual_ping("Test manual desde script de prueba")
    print(f"   Resultado: {'✅ Éxito' if result else '❌ Error'}")
    
    # Prueba 4: Ping de error (solo para testing)
    print("\n⚠️  Prueba 4: Ping de error (para testing)")
    result = await heartbeat.send_ping("fail", "Test de error - esto es solo una prueba")
    print(f"   Resultado: {'✅ Éxito' if result else '❌ Error'}")
    
    # Mostrar estado del sistema
    print("\n📊 Estado del sistema:")
    status = heartbeat.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Ping final de éxito para limpiar el estado de error
    print("\n🔄 Enviando ping final de éxito...")
    await heartbeat.send_ping("success", "Test completado - sistema funcionando correctamente")
    
    print("\n✅ Todas las pruebas completadas!")
    print("🔔 Si has configurado alertas, deberías haber recibido notificaciones.")
    
    return True


async def continuous_test():
    """Prueba continua para testing del monitoreo"""
    print("🔄 Iniciando prueba continua...")
    print("   Presiona Ctrl+C para detener")
    
    heartbeat_url = os.getenv('HEALTHCHECKS_PING_URL')
    if not heartbeat_url:
        print("❌ Error: HEALTHCHECKS_PING_URL no está configurado")
        return
    
    heartbeat = HeartbeatSystem(heartbeat_url, interval=30)  # 30 segundos para testing
    
    try:
        # Enviar ping inicial
        await heartbeat.send_ping("start", "Iniciando prueba continua")
        
        # Loop de prueba
        count = 0
        while True:
            count += 1
            await asyncio.sleep(30)  # Esperar 30 segundos
            
            message = f"Prueba continua - ping #{count}"
            result = await heartbeat.send_ping("success", message)
            
            print(f"🔄 Ping #{count}: {'✅' if result else '❌'} - {message}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Deteniendo prueba continua...")
        await heartbeat.send_ping("fail", "Prueba continua terminada")
        print("✅ Prueba detenida")


def show_help():
    """Mostrar ayuda"""
    print("Script de Prueba del Sistema de Heartbeats")
    print("=" * 50)
    print("Uso: python3 test_heartbeat.py [comando]")
    print()
    print("Comandos disponibles:")
    print("  test        - Ejecutar pruebas básicas (por defecto)")
    print("  continuous  - Ejecutar prueba continua")
    print("  help        - Mostrar esta ayuda")
    print()
    print("Configuración requerida:")
    print("  HEALTHCHECKS_PING_URL en archivo .env")


async def main():
    """Función principal"""
    # Verificar argumentos
    command = sys.argv[1] if len(sys.argv) > 1 else "test"
    
    if command == "help":
        show_help()
        return
    elif command == "test":
        await test_heartbeat()
    elif command == "continuous":
        await continuous_test()
    else:
        print(f"❌ Comando desconocido: {command}")
        show_help()


if __name__ == "__main__":
    asyncio.run(main())
