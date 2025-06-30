#!/bin/bash

# Script de inicio para el Discord Message Listener
echo "🚀 Iniciando Discord Message Listener..."
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

# Instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
pip3 install -r requirements.txt

# Ejecutar el listener
echo "🎧 Iniciando listener..."
python3 simple_message_listener.py
