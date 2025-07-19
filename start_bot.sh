#!/bin/bash

# Script de inicio para el Discord Self-Bot (Real-time monitoring)
echo "🚀 Iniciando Discord Self-Bot en modo tiempo real..."
echo "=========================================="

# Verificar que existe el archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado!"
    echo "📝 Copia .env.example a .env y configura tu token:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar que pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 no está instalado"
    exit 1
fi

# Activar el entorno virtual si existe
if [ -d "discord_selfbotting" ]; then
    echo "🐍 Activando entorno virtual..."
    source discord_selfbotting/bin/activate
fi

# Instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
pip3 install -r requirements.txt

# Mostrar información del modo
echo ""
echo "🔴 MODO: Monitoreo en tiempo real"
echo "📝 El bot procesará NUEVOS MENSAJES que lleguen a partir de ahora"
echo "💡 Para detener el bot, presiona Ctrl+C"
echo ""

# Ejecutar el bot
echo "🎧 Iniciando bot..."
python3 simple_message_listener.py
