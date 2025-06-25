# Discord Self-Bot (Python)

Un bot de Discord para automatización y monitoreo de mensajes, ahora en Python.

## Características

- Monitoreo y registro de mensajes
- Sistema de comandos con soporte de prefijo
- Eliminación de mensajes
- Información y estadísticas del bot
- Verificación de latencia

## Configuración

### Para desarrollo local:

1. Clona el repositorio
2. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o
   venv\Scripts\activate     # Windows
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Agrega tu token de Discord en el archivo `.env`:
   ```env
   DISCORD_TOKEN=tu_token_aqui
   PREFIX=!
   ```

5. Configura los ajustes del bot en `config.py`

6. Inicia el bot:
   ```bash
   # Usando los scripts de desarrollo
   ./dev/start_bot.sh          # Con validaciones
   ./dev/start_bot_simple.sh   # Ejecución directa
   
   # O manualmente
   python main.py
   ```

### Para despliegue en servidor:

1. **Primera vez - Preparar el servidor:**
   ```bash
   # Conectar al servidor
   ssh tu_usuario@tu_servidor
   
   # Clonar el repositorio
   cd /opt
   sudo git clone https://github.com/tu_usuario/DiscordSelfBotting.git discord-bot
   cd discord-bot
   
   # Ejecutar script de preparación
   sudo bash prepare-server.sh
   ```

2. **Configurar GitHub Secrets** (ver sección más abajo)

3. **El deployment es automático** - Se ejecuta cuando haces push a main

### Migración desde discord-bot a deployuser:

Si ya tenías el bot configurado con el usuario `discord-bot`:

```bash
# En el servidor
cd /opt/discord-bot
sudo bash migrate-to-deployuser.sh
```

## GitHub Secrets

Para el deployment automático, configura estos secrets en tu repositorio de GitHub:

**Settings → Secrets and variables → Actions → New repository secret**

- `DISCORD_TOKEN`: Tu token de Discord
- `LINODE_HOST`: IP de tu servidor  
- `LINODE_USERNAME`: `deployuser` (usuario configurado por el script)
- `SSH_PRIVATE_KEY`: Tu clave SSH privada

### ¿Cómo obtener tu clave SSH privada?

```bash
# En tu máquina local
cat ~/.ssh/id_rsa
# Copia todo el contenido (incluyendo -----BEGIN y -----END)
```

Edita `config.py` para configurar:
- Ajustes del bot
- Opciones de monitoreo de mensajes
- IDs de servidor y canal

## Estructura del Proyecto

```
├── main.py              # Archivo principal del bot
├── config.py            # Configuración del bot
├── requirements.txt     # Dependencias de Python
├── start_bot.sh        # Script de inicio
├── .env.example        # Ejemplo de archivo de entorno
├── utils/
│   └── logger.py       # Logger de mensajes
├── logs/               # Directorio de logs
└── discord_selfbotting/ # Entorno virtual de Python
```