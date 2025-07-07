#!/bin/bash

# Script de inicio mejorado para el Discord Message Listener
# Incluye verificaciones de configuración y manejo de errores

echo "🚀 Iniciando Discord Message Listener Mejorado"
echo "================================================"

# Verificar que existe el archivo .env
if [ ! -f .env ]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "   Crea un archivo .env con tus tokens y configuración"
    echo "   Ejemplo:"
    echo "   DISCORD_TOKEN=tu_token_aqui"
    echo "   NOTION_TOKEN=tu_notion_token"
    echo "   NOTION_DATABASE_ID=tu_database_id"
    echo "   MONITORING_SERVER_ID=123456789012345678"
    exit 1
fi

# Verificar que Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    exit 1
fi

# Verificar que las dependencias están instaladas
echo "📦 Verificando dependencias..."
if ! python3 -c "import discord, notion_client, dotenv" 2>/dev/null; then
    echo "⚠️  Instalando dependencias faltantes..."
    pip3 install -r requirements.txt
fi

# Verificar configuración de Notion (opcional)
echo "🔧 Verificando configuración de Notion..."
python3 setup_notion_database.py

read -p "¿Continuar con el inicio del bot? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelado por el usuario"
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p logs

echo "🤖 Iniciando bot..."
echo "   Presiona Ctrl+C para detener"
echo "================================================"

# Ejecutar el bot con manejo de errores
python3 simple_message_listener.py

echo "👋 Bot terminado"
