#!/bin/bash

echo "🚀 Configuración rápida del Discord Message Processor"
echo ""

# Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Instálalo primero."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
echo "✅ Python encontrado: $python_version"

# Crear entorno virtual si no existe
if [ ! -d "discord_selfbotting" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv discord_selfbotting
    
    if [ $? -eq 0 ]; then
        echo "✅ Entorno virtual creado"
    else
        echo "❌ Error creando entorno virtual"
        exit 1
    fi
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source discord_selfbotting/bin/activate

# Verificar/crear requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "📝 Creando requirements.txt..."
    cat > requirements.txt << 'EOF'
discord.py-self==2.1.0b5113+g71609f4f
notion-client==2.2.1
python-dotenv==1.0.0
aiohttp==3.12.13
EOF
    echo "✅ requirements.txt creado"
fi

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas correctamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Verificar/crear directorio de logs
echo "📁 Configurando directorio de logs..."
mkdir -p logs
echo "✅ Directorio logs creado"

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Archivo .env no encontrado. Creando plantilla..."
    
    cat > .env << 'EOF'
# Discord Configuration (OBLIGATORIO)
DISCORD_TOKEN=tu_token_aqui
MONITORING_SERVER_ID=id_del_servidor

# Channel Configuration (OPCIONAL)
# Si no se especifica, procesa todos los canales del servidor
MONITORING_CHANNEL_IDS=canal1_id,canal2_id

# Notion Configuration (OPCIONAL)
# Si no se especifica, solo guarda en archivo JSON
NOTION_TOKEN=tu_token_notion
NOTION_DATABASE_ID=id_database_notion

# Heartbeat Configuration (OPCIONAL)
HEALTHCHECKS_PING_URL=https://hc-ping.com/tu-uuid
HEARTBEAT_INTERVAL=300

# Log Configuration (OPCIONAL)
LOG_FILE=./logs/messages.json
EOF
    
    echo "✅ Archivo .env creado con plantilla"
    echo ""
    echo "🔧 IMPORTANTE: Edita el archivo .env con tus configuraciones:"
    echo "   - DISCORD_TOKEN: Tu token de Discord"
    echo "   - MONITORING_SERVER_ID: ID del servidor a monitorear"
    echo "   - Opcionalmente: tokens de Notion y otros parámetros"
    echo ""
    echo "📖 Consulta README.md para más detalles"
else
    echo "✅ Archivo .env ya existe"
fi

# Hacer scripts ejecutables
echo "🔐 Configurando permisos..."
chmod +x start_bot.sh 2>/dev/null || true
chmod +x start_monitor.sh 2>/dev/null || true
chmod +x setup.sh 2>/dev/null || true

echo ""
echo "🎉 Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env con tus configuraciones"
echo "2. Ejecuta: ./start_bot.sh"
echo ""
echo "📚 Archivos importantes:"
echo "   - .env: Configuraciones"
echo "   - README.md: Documentación completa"
echo "   - start_bot.sh: Script de inicio en tiempo real"
echo "   - start_monitor.sh: Script de monitoreo independiente"
echo ""
echo "🚀 ¡Listo para monitorear mensajes en tiempo real!"
