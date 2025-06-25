# Discord Self-Bot (Python)

Un bot de Discord para automatización y monitoreo de mensajes, ahora en Python.

## Características

- Monitoreo y registro de mensajes
- Sistema de comandos con soporte de prefijo
- Eliminación de mensajes
- Información y estadísticas del bot
- Verificación de latencia

## Configuración

1. Clona el repositorio
2. Asegúrate de que el entorno virtual de Python esté configurado:
   ```bash
   # El entorno ya está configurado en discord_selfbotting/
   source discord_selfbotting/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` con tu token de Discord:
   ```bash
   cp .env .env
   nano .env
   ```
   
   Contenido del `.env`:
   ```env
   DISCORD_TOKEN=tu_token_aqui
   PREFIX=!
   ```

5. Configura los ajustes del bot en `config.py`

6. Inicia el bot:
   ```bash
   # Usando el script de inicio
   ./start_bot.sh
   
   # O manualmente
   python main.py
   ```

## Configuración

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