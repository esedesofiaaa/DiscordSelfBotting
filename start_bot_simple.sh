#!/bin/bash

# Script simple para ejecutar el bot sin validaciones

echo "🐍 Ejecutando bot de Discord (modo debug)..."

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ejecutar directamente con el Python del entorno virtual
"$SCRIPT_DIR/discord_selfbotting/bin/python" "$SCRIPT_DIR/main.py"
