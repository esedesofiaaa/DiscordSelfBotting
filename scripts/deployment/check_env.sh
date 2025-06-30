#!/bin/bash

# Script para verificar el entorno y configuración

echo "🔍 Verificando entorno de Discord Bot..."
echo

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📂 Directorio actual: $SCRIPT_DIR"
echo

# Verificar Python del entorno virtual
PYTHON_PATH="$SCRIPT_DIR/discord_selfbotting/bin/python"
if [ -f "$PYTHON_PATH" ]; then
    echo "✅ Python del entorno virtual encontrado"
    echo "🐍 Versión: $("$PYTHON_PATH" --version)"
    echo "📁 Ruta: $PYTHON_PATH"
else
    echo "❌ Python del entorno virtual NO encontrado"
fi
echo

# Verificar archivos principales
echo "📋 Verificando archivos principales:"
for file in "main.py" "config.py" "requirements.txt" ".env"; do
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (no encontrado)"
    fi
done
echo

# Verificar dependencias
echo "📦 Verificando dependencias instaladas:"
if [ -f "$PYTHON_PATH" ]; then
    "$PYTHON_PATH" -c "import discord; print('✅ discord.py-self instalado')" 2>/dev/null || echo "❌ discord.py-self NO instalado"
    "$PYTHON_PATH" -c "import dotenv; print('✅ python-dotenv instalado')" 2>/dev/null || echo "❌ python-dotenv NO instalado"
else
    echo "❌ No se puede verificar (Python no encontrado)"
fi
echo

# Verificar configuración
echo "⚙️ Verificando configuración:"
if [ -f "$SCRIPT_DIR/.env" ]; then
    if grep -q "DISCORD_TOKEN=" "$SCRIPT_DIR/.env"; then
        if grep -q "DISCORD_TOKEN=1384570203022692392" "$SCRIPT_DIR/.env"; then
            echo "⚠️ Token configurado como ID de usuario (necesita token real)"
        else
            echo "✅ Token configurado (valor diferente al ID por defecto)"
        fi
    else
        echo "❌ DISCORD_TOKEN no encontrado en .env"
    fi
else
    echo "❌ Archivo .env no encontrado"
fi
echo

echo "🎯 Para ejecutar el bot:"
echo "   ./start_bot.sh          (con validaciones)"
echo "   ./start_bot_simple.sh   (ejecución directa)"
