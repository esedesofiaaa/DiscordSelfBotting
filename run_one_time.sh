#!/bin/bash

# Script para ejecutar el bot Discord una sola vez
# Procesa todos los mensajes desde el 1 de julio hasta la fecha actual

echo "🚀 Iniciando procesamiento único de mensajes de Discord..."
echo "📅 Procesando mensajes desde el 1 de julio de 2025 hasta la fecha actual"
echo "⚠️  Este proceso puede tomar varios minutos dependiendo del número de mensajes"
echo ""

# Activar el entorno virtual si existe
if [ -d "discord_selfbotting" ]; then
    echo "🐍 Activando entorno virtual..."
    source discord_selfbotting/bin/activate
fi

# Verificar que existe el archivo principal
if [ ! -f "simple_message_listener.py" ]; then
    echo "❌ Error: No se encuentra el archivo simple_message_listener.py"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Error: No se encuentra el archivo .env con las configuraciones"
    echo "   Crea un archivo .env con las siguientes variables:"
    echo "   DISCORD_TOKEN=tu_token_aqui"
    echo "   MONITORING_SERVER_ID=id_del_servidor"
    echo "   MONITORING_CHANNEL_IDS=id1,id2,id3 (opcional)"
    echo "   NOTION_TOKEN=tu_token_notion (opcional)"
    echo "   NOTION_DATABASE_ID=id_database_notion (opcional)"
    echo "   HEALTHCHECKS_PING_URL=url_heartbeat (opcional)"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p logs

echo "▶️  Ejecutando el bot..."
echo "📝 Los mensajes se guardarán en logs/messages.json"
echo ""

# Ejecutar el bot
python3 simple_message_listener.py

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Procesamiento completado exitosamente!"
    echo "📊 Revisa el archivo logs/messages.json para ver los mensajes procesados"
    
    # Mostrar estadísticas del archivo si existe
    if [ -f "logs/messages.json" ]; then
        echo ""
        echo "📈 Estadísticas del archivo generado:"
        echo "   Tamaño: $(du -h logs/messages.json | cut -f1)"
        
        # Contar mensajes en el JSON si jq está disponible
        if command -v jq &> /dev/null; then
            message_count=$(jq '. | length' logs/messages.json 2>/dev/null || echo "?")
            echo "   Mensajes procesados: $message_count"
        fi
    fi
else
    echo ""
    echo "❌ Error durante el procesamiento"
    echo "   Revisa los mensajes de error anteriores"
    exit 1
fi

echo ""
echo "🏁 Proceso finalizado"
