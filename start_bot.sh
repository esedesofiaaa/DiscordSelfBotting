#!/bin/bash

# Script para ejecutar el bot de Discord en Python

echo "🐍 Iniciando bot de Discord en Python..."

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ruta del ejecutable Python del entorno virtual
PYTHON_PATH="$SCRIPT_DIR/discord_selfbotting/bin/python"

# Verificar que el entorno virtual existe
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Entorno virtual no encontrado en: $PYTHON_PATH"
    echo "📋 Ejecuta el siguiente comando para configurar el entorno:"
    echo "   python -m venv discord_selfbotting"
    echo "   source discord_selfbotting/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Verificar que existe el archivo main.py
if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "❌ Archivo main.py no encontrado!"
    exit 1
fi

# Verificar que existe el archivo .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo "❌ Archivo .env no encontrado!"
    echo "📋 Copia .env.example a .env y configura tu token:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Verificar que el token no sea el ID de usuario por defecto
if grep -q "DISCORD_TOKEN=1384570203022692392" "$SCRIPT_DIR/.env"; then
    echo "❌ Token de Discord no configurado correctamente!"
    echo "📋 El valor actual es tu ID de usuario, no tu token."
    echo "🔑 Necesitas obtener tu token real de Discord:"
    echo "   1. Abre Discord en el navegador"
    echo "   2. Presiona F12 -> Network tab"
    echo "   3. Envía un mensaje o actualiza"
    echo "   4. Busca 'Authorization' en los headers"
    echo "   5. Copia el token y ponlo en .env"
    echo ""
    echo "⚠️  ADVERTENCIA: Los self-bots van contra los ToS de Discord"
    exit 1
fi

# Mostrar información del entorno
echo "📂 Directorio de trabajo: $SCRIPT_DIR"
echo "🐍 Python ejecutable: $PYTHON_PATH"

# Ejecutar el bot usando la ruta absoluta del Python del entorno virtual
echo "🚀 Ejecutando bot..."
"$PYTHON_PATH" "$SCRIPT_DIR/main.py"
