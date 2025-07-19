# Discord Self-Bot Message Listener

Un bot de Discord que escucha y registra todos los mensajes de un servidor o canales específicos. **Ahora con integración directa a Notion!**

## 🚀 Características

- ✅ **Monitoreo en tiempo real** de mensajes de Discord
- ✅ **Integración directa con Notion** - Guarda mensajes en una base de datos de Notion
- ✅ **Sistema de backup** - Archivo de texto como respaldo cuando Notion no está disponible
- ✅ **Filtrado por servidor y canales** específicos
- ✅ **Información completa** - Autor, fecha, servidor, canal, contenido, archivos adjuntos, URLs
- ✅ **Fácil configuración** con archivos `.env`
- ✅ **Manejo robusto de errores** con múltiples métodos de respaldo
- ✅ **Sistema de monitoreo de heartbeats** - Alertas automáticas con Healthchecks.io
- ✅ **Auto-reinicio** - Monitor independiente que reinicia el bot si se cae
- ✅ **Monitoreo dual** - Bot principal + monitor independiente para máxima confiabilidad

## 📋 Requisitos

- Python 3.8+
- Token de Discord (self-bot)
- **Opcional**: Cuenta de Notion con API access para la integración

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd DiscordSelfBotting
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Edita el archivo .env con tus configuraciones
```

## ⚙️ Configuración

### Configuración Básica (Discord)

Edita el archivo `.env`:

```env
# Token de Discord
DISCORD_TOKEN=tu_token_de_discord_aquí

# Servidor a monitorear
MONITORING_SERVER_ID=id_del_servidor

# Canales específicos (opcional)
MONITORING_CHANNEL_IDS=canal1_id,canal2_id

# Archivo de backup
LOG_FILE=./logs/messages.txt
```

### 🆕 Configuración de Notion (Nuevo!)

Para guardar mensajes directamente en Notion, añade estas líneas a tu `.env`:

```env
# Token de integración de Notion
NOTION_TOKEN=secret_tu_notion_token_aquí

# ID de la base de datos de Notion
NOTION_DATABASE_ID=tu_database_id_aquí
```

**📖 Para configuración detallada de Notion, consulta [README_NOTION.md](README_NOTION.md)**

## 🧪 Verificar Configuración

### Probar integración con Notion
```bash
python test_notion.py
```

Este script verificará:
- ✅ Conexión con la API de Notion
- ✅ Acceso a tu base de datos
- ✅ Creación de una página de prueba

## 🚀 Uso

### Ejecutar el bot básico
```bash
python simple_message_listener.py
```

O usando el script de inicio:
```bash
./start_bot.sh
```

### Sistema de Monitoreo con Heartbeats

Para máxima confiabilidad, usa el sistema de monitoreo integrado:

```bash
# Probar conexión con Healthchecks.io
python3 test_heartbeat.py

# Iniciar bot con heartbeats automáticos
./start_bot.sh

# Iniciar monitor independiente (recomendado para producción)
./start_monitor.sh start

# Ver estado del monitor
./start_monitor.sh status

# Ver logs del monitor
./start_monitor.sh logs
```

**📖 Documentación completa**: Ver [README_HEARTBEATS.md](README_HEARTBEATS.md)

### Ejecutar como servicio (Linux)
```bash
# Instalar el servicio del bot
sudo cp discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# Instalar el servicio del monitor (opcional)
sudo cp discord-bot-monitor.service /etc/systemd/system/
sudo systemctl enable discord-bot-monitor
sudo systemctl start discord-bot-monitor

# Ver logs
sudo systemctl status discord-bot
sudo journalctl -fu discord-bot
```

## 📊 Datos Capturados

Cada mensaje registrado incluye:

| Campo | Descripción | Ubicación |
|-------|-------------|-----------|
| **Autor** | Nombre del usuario que envió el mensaje | Notion + archivo |
| **Fecha** | Timestamp del mensaje | Notion + archivo |
| **Servidor** | Nombre del servidor de Discord | Notion + archivo |
| **Canal** | Nombre del canal donde se envió | Notion + archivo |
| **Contenido** | Texto del mensaje | Notion + archivo |
| **URL adjunta** | Primera URL encontrada en el mensaje | Solo Notion |
| **Archivo Adjunto** | Información sobre archivos adjuntos | Notion + archivo |
| **URL del mensaje** | Enlace directo al mensaje en Discord | Solo Notion |

## 📁 Estructura del Proyecto

```
DiscordSelfBotting/
├── simple_message_listener.py   # Bot principal con integración Notion
├── test_notion.py              # Script de prueba para Notion
├── requirements.txt            # Dependencias Python
├── .env.example               # Plantilla de configuración
├── README_NOTION.md           # Guía detallada de Notion
├── logs/                      # Archivos de backup
│   └── messages.txt
└── scripts/                   # Scripts de deployment
```

## 🔄 Sistema de Respaldo

El bot implementa un sistema de respaldo robusto:

1. **Primario**: Mensajes se guardan en Notion
2. **Secundario**: Si Notion falla, se guarda en archivo de texto
3. **Logs**: Consola muestra el estado en tiempo real

## 🛡️ Seguridad

- ❌ **Nunca compartas tu token de Discord**
- ❌ **Nunca subas el archivo `.env` a repositorios públicos**
- ✅ **Usa el archivo `.env.example` como plantilla**
- ✅ **Revisa los permisos de tu integración de Notion**

## 🐛 Solución de Problemas

### Bot no se conecta
- Verifica que el token de Discord sea válido
- Asegúrate de que el bot tenga acceso al servidor

### Notion no funciona
- Ejecuta `python test_notion.py` para diagnosticar
- Verifica que la integración esté compartida con la base de datos
- Revisa que las propiedades de la base de datos sean correctas

### Mensajes no se registran
- Verifica que el ID del servidor sea correcto
- Comprueba que los IDs de canales sean válidos
- Revisa los logs en la consola para errores específicos

## 📚 Documentación Adicional

- [README_NOTION.md](README_NOTION.md) - Configuración detallada de Notion
- [README_SIMPLE_LISTENER.md](README_SIMPLE_LISTENER.md) - Información del bot original
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía de despliegue en servidor

## ⚖️ Términos de Uso

Este proyecto es para uso educativo y personal. Asegúrate de cumplir con los Términos de Servicio de Discord y las políticas de uso de Notion.

## 📝 Changelog

### v2.0.0 (Julio 2025)
- ✨ **Nueva integración directa con Notion**
- ✨ **Sistema de respaldo automático**
- ✨ **Script de prueba para verificar configuración**
- ✨ **Documentación mejorada**
- 🔧 **Manejo robusto de errores**

### v1.0.0
- ✅ Bot básico de escucha de mensajes
- ✅ Guardado en archivo de texto
- ✅ Filtrado por servidor y canales
