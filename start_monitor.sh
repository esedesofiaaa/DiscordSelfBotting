#!/bin/bash
# Script de inicio para el monitor del bot de Discord
# Este script inicia el monitor independiente que supervisa el bot principal

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
MONITOR_LOG="$LOG_DIR/monitor.log"
PID_FILE="$LOG_DIR/monitor.pid"

# Crear directorio de logs si no existe
mkdir -p "$LOG_DIR"

# Función para mostrar ayuda
show_help() {
    echo "Monitor del Bot de Discord - Sistema de Monitoreo"
    echo "Uso: $0 [start|stop|restart|status|logs]"
    echo ""
    echo "Comandos:"
    echo "  start   - Iniciar el monitor"
    echo "  stop    - Detener el monitor"
    echo "  restart - Reiniciar el monitor"
    echo "  status  - Mostrar estado del monitor"
    echo "  logs    - Mostrar logs del monitor"
    echo "  test    - Probar conexión con Healthchecks.io"
}

# Función para verificar si el monitor está corriendo
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Función para iniciar el monitor
start_monitor() {
    if is_running; then
        echo "❌ El monitor ya está en ejecución (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    echo "🚀 Iniciando monitor del bot..."
    
    # Verificar que Python está disponible
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python3 no está instalado"
        return 1
    fi
    
    # Verificar que el archivo del monitor existe
    if [ ! -f "$SCRIPT_DIR/monitor_bot.py" ]; then
        echo "❌ monitor_bot.py no encontrado"
        return 1
    fi
    
    # Cargar variables de entorno si existe el archivo .env
    if [ -f "$SCRIPT_DIR/.env" ]; then
        export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
    fi
    
    # Iniciar el monitor en background
    cd "$SCRIPT_DIR"
    nohup python3 monitor_bot.py >> "$MONITOR_LOG" 2>&1 &
    
    # Guardar PID
    echo $! > "$PID_FILE"
    
    # Verificar que se inició correctamente
    sleep 2
    if is_running; then
        echo "✅ Monitor iniciado correctamente (PID: $(cat "$PID_FILE"))"
        echo "📁 Logs en: $MONITOR_LOG"
        return 0
    else
        echo "❌ Error al iniciar el monitor"
        return 1
    fi
}

# Función para detener el monitor
stop_monitor() {
    if ! is_running; then
        echo "⚠️ El monitor no está en ejecución"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    echo "⏹️ Deteniendo monitor (PID: $PID)..."
    
    # Intentar terminar graciosamente
    kill -TERM "$PID" 2>/dev/null
    
    # Esperar hasta 10 segundos
    for i in {1..10}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    
    # Si aún está corriendo, forzar terminación
    if kill -0 "$PID" 2>/dev/null; then
        echo "💀 Forzando terminación..."
        kill -KILL "$PID" 2>/dev/null
    fi
    
    # Limpiar archivo PID
    rm -f "$PID_FILE"
    echo "✅ Monitor detenido"
}

# Función para mostrar estado
show_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo "✅ Monitor en ejecución (PID: $PID)"
        
        # Mostrar información del proceso
        if command -v ps &> /dev/null; then
            echo "📊 Información del proceso:"
            ps -p "$PID" -o pid,ppid,cmd,%cpu,%mem,etime 2>/dev/null || echo "   No se pudo obtener información del proceso"
        fi
        
        # Mostrar últimas líneas del log
        if [ -f "$MONITOR_LOG" ]; then
            echo ""
            echo "📋 Últimas líneas del log:"
            tail -n 5 "$MONITOR_LOG"
        fi
    else
        echo "❌ Monitor no está en ejecución"
    fi
}

# Función para mostrar logs
show_logs() {
    if [ -f "$MONITOR_LOG" ]; then
        echo "📋 Logs del monitor:"
        tail -n 50 "$MONITOR_LOG"
    else
        echo "❌ Archivo de log no encontrado: $MONITOR_LOG"
    fi
}

# Función para probar heartbeats
test_heartbeat() {
    echo "🧪 Probando conexión con Healthchecks.io..."
    cd "$SCRIPT_DIR"
    python3 -c "
import asyncio
from heartbeat_system import HeartbeatSystem
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    url = os.getenv('HEALTHCHECKS_PING_URL', 'https://hc-ping.com/f679a27c-8a41-4ae2-9504-78f1b260e71d')
    heartbeat = HeartbeatSystem(url)
    result = await heartbeat.send_manual_ping('Test desde script de monitor')
    print('✅ Ping enviado exitosamente' if result else '❌ Error al enviar ping')
    status = heartbeat.get_status()
    print(f'📊 Estado: {status}')

asyncio.run(test())
"
}

# Función para reiniciar
restart_monitor() {
    echo "🔄 Reiniciando monitor..."
    stop_monitor
    sleep 2
    start_monitor
}

# Procesar argumentos
case "${1:-}" in
    start)
        start_monitor
        ;;
    stop)
        stop_monitor
        ;;
    restart)
        restart_monitor
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        test_heartbeat
        ;;
    *)
        show_help
        ;;
esac
