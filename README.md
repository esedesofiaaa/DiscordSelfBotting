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

1. Ejecuta el script de configuración:
   ```bash
   sudo bash setup-linode.sh
   ```

2. El token se configura automáticamente desde GitHub Secrets durante el deployment.

## GitHub Secrets

Para el despliegue automático, configura estos secrets en tu repositorio:

- `DISCORD_TOKEN`: Tu token de Discord
- `LINODE_HOST`: IP de tu servidor
- `LINODE_USERNAME`: Usuario para SSH (ej: deployuser)
- `SSH_PRIVATE_KEY`: Tu clave SSH privada

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