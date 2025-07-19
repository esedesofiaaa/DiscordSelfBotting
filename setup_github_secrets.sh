#!/bin/bash

# Script para ayudar a configurar secretos de GitHub Actions
# Este script NO expone información sensible, solo ayuda con el formato

echo "🔐 GitHub Actions Setup Helper"
echo "=============================="
echo ""

echo "📋 Este script te ayuda a preparar los secretos para GitHub Actions"
echo ""

# Verificar si existe credentials.json
if [ -f "credentials.json" ]; then
    echo "✅ Archivo credentials.json encontrado"
    echo ""
    echo "📄 Para configurar GOOGLE_DRIVE_CREDENTIALS_JSON en GitHub:"
    echo "   1. Ve a tu repositorio → Settings → Secrets and variables → Actions"
    echo "   2. Crea un nuevo Repository secret llamado: GOOGLE_DRIVE_CREDENTIALS_JSON"
    echo "   3. Copia y pega TODO el contenido del archivo credentials.json"
    echo ""
    echo "🔍 Vista previa del formato (primeras líneas):"
    head -n 3 credentials.json
    echo "   ..."
    echo ""
else
    echo "❌ Archivo credentials.json no encontrado"
    echo "   Descarga las credenciales desde Google Cloud Console"
    echo "   y guárdalas como 'credentials.json' en este directorio"
    echo ""
fi

# Verificar si existe token.json
if [ -f "token.json" ]; then
    echo "✅ Archivo token.json encontrado (autorización completada)"
    echo ""
    echo "📄 Para configurar GOOGLE_DRIVE_TOKEN_JSON en GitHub:"
    echo "   1. Ve a tu repositorio → Settings → Secrets and variables → Actions"
    echo "   2. Crea un nuevo Repository secret llamado: GOOGLE_DRIVE_TOKEN_JSON"
    echo "   3. Copia y pega TODO el contenido del archivo token.json"
    echo ""
    echo "🔍 Vista previa del formato (token oculto por seguridad):"
    echo '{"token": "[HIDDEN]", "refresh_token": "[HIDDEN]", "token_uri": "https://oauth2.googleapis.com/token", ...}'
    echo ""
else
    echo "❌ Archivo token.json no encontrado"
    echo "   ⚠️  DEBES autorizar Google Drive primero:"
    echo ""
    echo "   python3 -c \""
    echo "from google_drive_manager import GoogleDriveManager"
    echo "import asyncio"
    echo ""
    echo "async def authorize():"
    echo "    manager = GoogleDriveManager()"
    echo "    success = await manager.initialize()"
    echo "    if success:"
    echo "        print('✅ Autorización completada!')"
    echo "    else:"
    echo "        print('❌ Error en la autorización')"
    echo ""
    echo "asyncio.run(authorize())"
    echo "   \""
    echo ""
fi

# Verificar .env
if [ -f ".env" ]; then
    echo "✅ Archivo .env encontrado"
    echo ""
    echo "📊 Variables extraídas de tu .env actual:"
    echo "   (Configura estas como Repository Variables en GitHub Actions)"
    echo ""
    
    # Extraer variables que van como Variables (no sensibles)
    echo "🔹 MONITORING_SERVER_ID: $(grep '^MONITORING_SERVER_ID=' .env | cut -d'=' -f2)"
    echo "🔹 MONITORING_CHANNEL_IDS: $(grep '^MONITORING_CHANNEL_IDS=' .env | cut -d'=' -f2)"
    echo "🔹 NOTION_DATABASE_ID: $(grep '^NOTION_DATABASE_ID=' .env | cut -d'=' -f2)"
    echo "🔹 HEARTBEAT_INTERVAL: $(grep '^HEARTBEAT_INTERVAL=' .env | cut -d'=' -f2)"
    echo "🔹 MONITOR_INTERVAL: $(grep '^MONITOR_INTERVAL=' .env | cut -d'=' -f2)"
    echo "🔹 BOT_PROCESS_NAME: $(grep '^BOT_PROCESS_NAME=' .env | cut -d'=' -f2)"
    echo "🔹 AUTO_RESTART_BOT: $(grep '^AUTO_RESTART_BOT=' .env | cut -d'=' -f2)"
    echo "🔹 GOOGLE_DRIVE_ENABLED: $(grep '^GOOGLE_DRIVE_ENABLED=' .env | cut -d'=' -f2)"
    echo "🔹 GOOGLE_DRIVE_FOLDER_ID: $(grep '^GOOGLE_DRIVE_FOLDER_ID=' .env | cut -d'=' -f2)"
    echo "🔹 GOOGLE_DRIVE_IMAGE_MODE: $(grep '^GOOGLE_DRIVE_IMAGE_MODE=' .env | cut -d'=' -f2)"
    echo ""
    
    echo "🔐 Secretos encontrados (configura como Repository Secrets):"
    echo "   (⚠️  NO se muestran los valores por seguridad)"
    echo ""
    
    if grep -q "^DISCORD_TOKEN=" .env; then
        echo "🔹 DISCORD_TOKEN: [CONFIGURADO]"
    else
        echo "🔹 DISCORD_TOKEN: [FALTANTE]"
    fi
    
    if grep -q "^NOTION_TOKEN=" .env; then
        echo "🔹 NOTION_TOKEN: [CONFIGURADO]"
    else
        echo "🔹 NOTION_TOKEN: [FALTANTE]"
    fi
    
    if grep -q "^HEALTHCHECKS_PING_URL=" .env; then
        echo "🔹 HEALTHCHECKS_PING_URL: [CONFIGURADO]"
    else
        echo "🔹 HEALTHCHECKS_PING_URL: [FALTANTE]"
    fi
    
else
    echo "❌ Archivo .env no encontrado"
    echo "   Crea el archivo .env primero usando:"
    echo "   cp .env.example .env"
    echo ""
fi

echo ""
echo "📚 Documentación completa: GITHUB_ACTIONS_SETUP.md"
echo "🚀 Una vez configurado, haz push a la rama 'main' para deployment automático"
echo ""
